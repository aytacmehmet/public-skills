from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = SKILL_ROOT / "scripts" / "scaffold_fiori_workspace.py"
VALIDATOR = SKILL_ROOT / "scripts" / "validate_fiori_delivery.py"
INSPECTOR = SKILL_ROOT / "scripts" / "inspect_abap_package.py"


def run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *(str(item) for item in arguments)],
        text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
    )


class SkillToolTests(unittest.TestCase):
    def create_rap_package(self, root: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / "z_c_order.ddls.asddls").write_text(
            """@UI.headerInfo: { typeName: 'Order', title: { value: 'OrderId' } }
@UI.lineItem: [{ position: 10, value: 'OrderId' }]
define root view entity Z_C_Order as projection on Z_I_Order {
  key OrderId,
  CustomerId,
  association [0..1] to Z_I_Customer as _Customer on $projection.CustomerId = _Customer.CustomerId
}
""",
            encoding="utf-8",
        )
        (root / "z_c_order.bdef.asbdef").write_text(
            """managed implementation in class zbp_c_order unique;
strict ( 2 );
with draft;
define behavior for Z_C_Order alias Order
persistent table zorder
lock master
authorization master ( instance )
etag master LastChangedAt {
  create; update; delete;
  action Approve result [1] $self;
  validation validateCustomer on save { field CustomerId; }
}
""",
            encoding="utf-8",
        )
        (root / "z_ui_order.srvd.srvdsrv").write_text(
            "define service Z_UI_ORDER { expose Z_C_Order as Orders; }",
            encoding="utf-8",
        )
        (root / "z_ui_order_o4.srvb.xml").write_text(
            "<serviceBinding><bindingType>ODATA V4</bindingType></serviceBinding>",
            encoding="utf-8",
        )
        (root / "z_c_order.dcls.asdcls").write_text(
            "define role ZR_ORDER { grant select on Z_C_Order where ( CustomerId ) = aspect pfcg_auth( Z_ORDER, CUSTOMER, ACTVT = '03' ); }",
            encoding="utf-8",
        )

    def inspect_complete_package(self, root: Path) -> Path:
        package = root / "abap"
        self.create_rap_package(package)
        backend = root / "backend.json"
        result = run(
            INSPECTOR, package, "--output", backend, "--package-name", "Z_ORDER",
            "--service-uri", "/sap/opu/odata4/sap/z_ui_order/srvd/sap/z_ui_order/0001/",
            "--protocol", "odata-v4",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return backend

    def test_code_scaffold_requires_explicit_architecture_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(SCAFFOLD, directory, "--app-id", "com.acme.app", "--name", "App", "--output", "code")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--framework is required", result.stderr)
        self.assertIn("--ui5-version is required", result.stderr)

    def test_interactive_scaffold_does_not_create_production_app(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "interactive")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "prototype" / "manifest.json").is_file())
            self.assertTrue((root / "prototype" / "Component-preload.js").is_file())
            css = (root / "prototype" / "css" / "app.css").read_text(encoding="utf-8")
            self.assertIn(".sapUiComponentContainer > div", css)
            self.assertFalse((root / "app").exists())
            contract = json.loads((root / "design-contract.json").read_text(encoding="utf-8"))
            self.assertEqual(contract["context"]["targetSystem"]["ui5Runtime"], "unknown")

    def test_png_scaffold_includes_prototype_and_requires_real_capture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold = run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "png")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            contract = json.loads((root / "design-contract.json").read_text(encoding="utf-8"))
            self.assertEqual(contract["project"]["outputs"], ["png", "interactive"])
            self.assertTrue((root / "prototype" / "manifest.json").is_file())
            result = run(VALIDATOR, root, "--allow-warnings", "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("PNG_MISSING", {item["code"] for item in payload["findings"]})

    def test_unicode_output_path_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "Türkçe Çıktı"
            result = run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "Uygulama", "--output", "interactive")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Türkçe Çıktı", result.stdout)

    def test_abap_package_contract_drives_code_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend = self.inspect_complete_package(root)
            backend_data = json.loads(backend.read_text(encoding="utf-8"))
            self.assertEqual(backend_data["recommendation"]["readiness"], "ready")
            self.assertEqual(backend_data["service"]["entitySet"], "Orders")
            self.assertIn("Approve", backend_data["behavior"]["actions"])
            self.assertEqual(backend_data["model"]["entities"][0]["fields"], ["OrderId", "CustomerId"])

            delivery = root / "delivery"
            scaffold = run(
                SCAFFOLD, delivery, "--app-id", "com.acme.orders", "--name", "Orders",
                "--output", "code", "--ui5-version", "1.151.0", "--backend-contract", backend,
            )
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            contract = json.loads((delivery / "design-contract.json").read_text(encoding="utf-8"))
            self.assertEqual(contract["architecture"]["framework"], "fiori-elements-odata-v4")
            self.assertEqual(contract["backendEvidence"]["status"], "source-verified")
            self.assertEqual(contract["dataContract"]["mainService"]["entitySet"], "Orders")
            validated = run(VALIDATOR, delivery, "--allow-warnings", "--json")
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

    def test_backend_contract_hash_tampering_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend = self.inspect_complete_package(root)
            delivery = root / "delivery"
            self.assertEqual(run(
                SCAFFOLD, delivery, "--app-id", "com.acme.orders", "--name", "Orders",
                "--output", "code", "--ui5-version", "1.151.0", "--backend-contract", backend,
            ).returncode, 0)
            copied = delivery / "abap-backend-contract.json"
            copied.write_text(copied.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            result = run(VALIDATOR, delivery, "--allow-warnings", "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("BACKEND_HASH", {item["code"] for item in payload["findings"]})

    def test_adt_snapshot_truncation_stays_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "snapshot.json"
            snapshot.write_text(json.dumps({
                "packageName": "Z_ORDER",
                "objectCount": 2,
                "objects": [{
                    "name": "Z_C_ORDER", "type": "DDLS/DF", "version": "active",
                    "truncated": True, "source": "define root view entity Z_C_Order as select from zorder { key id as OrderId }",
                }],
            }), encoding="utf-8")
            output = root / "backend.json"
            result = run(INSPECTOR, snapshot, "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["recommendation"]["readiness"], "partial")
            self.assertFalse(payload["source"]["complete"])
            self.assertTrue(any("truncated" in gap for gap in payload["gaps"]))

    def test_inspector_rejects_zip_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("../z_c_order.ddls.asddls", "define view entity Z_C_Order as select from zorder { key id }")
            result = run(INSPECTOR, archive, "--output", root / "backend.json")
            self.assertEqual(result.returncode, 2)
            self.assertIn("Unsafe ZIP member path", result.stderr)

    def test_validator_scans_delivery_even_when_root_is_named_resources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "resources"
            scaffold = run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "interactive")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            unsafe = root / "prototype" / "unsafe.js"
            unsafe.write_text("eval('unsafe')\n", encoding="utf-8")
            result = run(VALIDATOR, root, "--allow-warnings", "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("DANGEROUS_EVAL", {item["code"] for item in payload["findings"]})

    def test_validator_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "design-contract.json").write_text('{"project": {}, "project": {}}', encoding="utf-8")
            (root / "design-contract.schema.json").write_text("{}", encoding="utf-8")
            result = run(VALIDATOR, root, "--allow-warnings", "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Duplicate JSON key", payload["findings"][0]["message"])

    def test_validator_enforces_bundled_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold = run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "interactive")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            contract_path = root / "design-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["unexpectedRootProperty"] = True
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            result = run(VALIDATOR, root, "--allow-warnings", "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("SCHEMA_ADDITIONAL", {item["code"] for item in payload["findings"]})

    def test_contract_can_model_existing_odata_v2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold = run(SCAFFOLD, root, "--app-id", "com.acme.legacy", "--name", "Legacy", "--output", "interactive")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            contract_path = root / "design-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["architecture"]["serviceProtocol"] = "odata-v2"
            contract["dataContract"]["mainService"]["protocol"] = "odata-v2"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            result = run(VALIDATOR, root, "--allow-warnings", "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_warnings_fail_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold = run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "interactive")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            strict = run(VALIDATOR, root, "--json")
            relaxed = run(VALIDATOR, root, "--allow-warnings", "--json")
            self.assertEqual(strict.returncode, 1)
            self.assertEqual(relaxed.returncode, 0)


    def load_inspector(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("inspect_abap_package_under_test", INSPECTOR)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_service_binding_protocol_from_separate_type_and_version(self) -> None:
        module = self.load_inspector()
        # Structure modelled on abapGit and ADT service binding exports: type and version are separate.
        abapgit_style = (
            '<?xml version="1.0" encoding="utf-8"?><abapGit version="v1.0.0" serializer="LCL_OBJECT_SRVB" '
            'serializer_version="v1.0.0"><asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0"><asx:values>'
            "<SRVB><METADATA><NAME>Z_UI_ORDER_O4</NAME><TYPE>SRVB/SVB</TYPE></METADATA>"
            "<BINDING><TYPE>ODATA</TYPE><VERSION>V4</VERSION><CATEGORY>0</CATEGORY></BINDING>"
            "</SRVB></asx:values></asx:abap></abapGit>"
        )
        adt_style = '<srvb:serviceBinding><srvb:binding srvb:type="ODATA" srvb:version="V2" srvb:category="0"/></srvb:serviceBinding>'
        self.assertEqual(module.detect_binding_protocol(abapgit_style), "odata-v4")
        self.assertEqual(module.detect_binding_protocol(adt_style), "odata-v2")
        self.assertEqual(module.detect_binding_protocol("<bindingType>ODATA V4</bindingType>"), "odata-v4")
        self.assertEqual(module.detect_binding_protocol("<BINDING><TYPE>INA</TYPE><VERSION>V2</VERSION></BINDING>"), "unknown")
        self.assertEqual(module.detect_binding_protocol('<abapGit version="v1.0.0"><SRVB/></abapGit>'), "unknown")

        # The namespace URL of a one-line export must not be read as a // comment.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_rap_package(root / "abap")
            (root / "abap" / "z_ui_order_o4.srvb.xml").write_text(abapgit_style, encoding="utf-8")
            output = root / "backend.json"
            self.assertEqual(run(INSPECTOR, root / "abap", "--output", output).returncode, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["service"]["protocol"], "odata-v4")

    def test_behavior_definition_is_read_per_entity_and_statement(self) -> None:
        module = self.load_inspector()
        source = """managed implementation in class zbp_i_order unique;
strict ( 2 );
with draft;
define behavior for Z_I_Order alias Order
persistent table zorder draft table zorder_d
lock master total etag LastChangedAt
authorization master ( instance )
etag master LocalLastChangedAt
{
  create ( authorization : global );
  update ( features : instance );
  internal delete;
  association _Items { create ( features : instance ); with draft; }
  static factory action ( features : global ) CopyOrder parameter Z_A_Copy [1];
  action ( features : instance ) Approve result [1] $self;
  draft action Edit; draft action Activate optimized; draft action Discard; draft action Resume;
  draft determine action Prepare { validation validateCustomer; }
  validation validateCustomer on save { create; field CustomerId; }
  determination setDefaults on modify { create; }
  side effects { action Approve affects field Status; field Quantity affects field Amount; }
  mapping for zorder { OrderId = order_id; }
}
define behavior for Z_I_OrderItem alias Item
persistent table zorder_i draft table zorder_i_d
lock dependent by _Order
authorization dependent by _Order
{
  update;
  association _Order { with draft; }
}
"""
        order, item = module.parse_behavior_definitions(module.strip_comments(source, "BDEF"), "Z_I_ORDER", "z_i_order.bdef.asbdef")
        self.assertEqual(order["entity"], "Z_I_Order")
        self.assertEqual((order["create"], order["update"], order["delete"]), (True, True, True))
        self.assertEqual(order["actions"], ["CopyOrder", "Approve"])
        self.assertEqual(order["draftActions"], ["Edit", "Activate", "Discard", "Resume", "Prepare"])
        self.assertEqual(order["createByAssociation"], ["_Items"])
        self.assertEqual(order["dynamicFeatureControl"], ["update", "CopyOrder", "Approve"])
        self.assertEqual((order["etag"], order["totalEtag"]), ("LocalLastChangedAt", "LastChangedAt"))
        self.assertTrue(order["sideEffectsDeclared"] and order["draftEnabled"])
        self.assertEqual(order["validations"], ["validateCustomer"])
        self.assertEqual(item["entity"], "Z_I_OrderItem")
        self.assertEqual((item["create"], item["update"], item["delete"]), (False, True, False))
        self.assertEqual(item["actions"], [])
        self.assertEqual(item["authorization"], "declared")

        projection = """projection;
strict ( 2 );
use draft;
define behavior for Z_C_Order alias Order use etag
{
  use create; use update ( features : instance ); use delete;
  use action Approve; use action Edit; use action Activate; use action Discard; use action Resume; use action Prepare;
  use association _Items { create; with draft; }
}
"""
        (order,) = module.parse_behavior_definitions(projection, "Z_C_ORDER", "z_c_order.bdef.asbdef")
        self.assertEqual(order["implementation"], "projection")
        self.assertTrue(order["draftEnabled"])
        self.assertEqual((order["create"], order["update"], order["delete"]), (True, True, True))
        self.assertEqual(order["actions"], ["Approve"])
        self.assertEqual(order["draftActions"], ["Edit", "Activate", "Discard", "Resume", "Prepare"])
        self.assertEqual(order["createByAssociation"], ["_Items"])

    def test_projection_elements_survive_annotations_and_report_what_is_unreadable(self) -> None:
        module = self.load_inspector()
        source = """@EndUserText.label: 'Order // not a comment'
define root view entity Z_C_Order as projection on Z_I_Order
{
      @UI.lineItem: [{ position: 10, importance: #HIGH }, { type: #FOR_ACTION, dataAction: 'Approve', label: 'Approve' }]
      @UI.selectionField: [{ position: 10 }]
  key OrderId,
      @Semantics.amount.currencyCode: 'Currency' -- trailing comment, with a comma
      Amount,
      concat( FirstName, LastName ) as FullName, // another, comment
      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_Currency', element: 'Currency' } }]
      Currency,
      case when Status = 'A' then 'X' else '' end,
      _Items : redirected to composition child Z_C_OrderItem,
      _Customer
}
"""
        elements = module.projection_elements(module.strip_comments(source, "DDLS"))
        self.assertEqual(elements["fields"], ["OrderId", "Amount", "FullName", "Currency"])
        self.assertEqual(elements["keys"], ["OrderId"])
        self.assertEqual(elements["exposedAssociations"], ["_Items", "_Customer"])
        self.assertEqual(len(elements["unparsed"]), 1)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_rap_package(root / "abap")
            (root / "abap" / "z_c_order.ddls.asddls").write_text(source, encoding="utf-8")
            output = root / "backend.json"
            self.assertEqual(run(INSPECTOR, root / "abap", "--output", output, "--protocol", "odata-v4").returncode, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(any("could not be read lexically" in gap for gap in payload["gaps"]))
            self.assertNotEqual(payload["recommendation"]["readiness"], "ready")

    def test_ambiguous_service_or_entity_set_is_a_gap_not_a_guess(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "abap"
            self.create_rap_package(package)
            (package / "z_api_order.srvd.srvdsrv").write_text(
                "define service Z_API_ORDER { expose Z_C_Order as Order; expose Z_I_Customer as Customer; }", encoding="utf-8",
            )
            output = root / "backend.json"
            self.assertEqual(run(INSPECTOR, package, "--output", output).returncode, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["service"]["definition"], "unknown")
            self.assertEqual(payload["service"]["entitySet"], "unknown")
            self.assertEqual(payload["recommendation"]["framework"], "undecided")
            self.assertTrue(any("--service-definition" in gap for gap in payload["gaps"]))

            self.assertEqual(run(INSPECTOR, package, "--output", output, "--service-definition", "z_api_order").returncode, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["service"]["definition"], "Z_API_ORDER")
            self.assertEqual(payload["service"]["entitySet"], "Order")  # the only exposed root entity
            self.assertFalse(any("--service-definition" in gap or "--entity-set" in gap for gap in payload["gaps"]))

    def test_scaffold_profile_is_never_reported_as_target_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = (
                "--app-id", "com.acme.orders", "--name", "Orders", "--output", "code", "--ui5-version", "1.151.0",
                "--framework", "freestyle-sapui5", "--service-uri", "/sap/opu/odata4/orders/", "--entity-set", "Orders",
            )
            unknown = root / "unknown"
            self.assertEqual(run(SCAFFOLD, unknown, *common).returncode, 0)
            contract = json.loads((unknown / "design-contract.json").read_text(encoding="utf-8"))
            self.assertEqual(contract["context"]["targetSystem"]["ui5Runtime"], "unknown")
            self.assertEqual(contract["architecture"]["minUI5Version"], "1.151.0")
            findings = json.loads(run(VALIDATOR, unknown, "--json").stdout)["findings"]
            self.assertIn("context.targetSystem.ui5Runtime is not verified", {item["message"] for item in findings})

            older = run(SCAFFOLD, root / "older", *common, "--target-ui5-runtime", "1.136.7")
            self.assertEqual(older.returncode, 2)
            self.assertIn("above the observed target runtime", older.stderr)

            newer = root / "newer"
            self.assertEqual(run(SCAFFOLD, newer, *common, "--target-ui5-runtime", "1.152.1").returncode, 0)
            contract_path = newer / "design-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(contract["context"]["targetSystem"]["ui5Runtime"], "1.152.1")
            codes = {item["code"] for item in json.loads(run(VALIDATOR, newer, "--allow-warnings", "--json").stdout)["findings"]}
            self.assertFalse(codes & {"SEMANTIC_UI5_VERSION", "SEMANTIC_MIN_UI5"})
            contract["context"]["targetSystem"]["ui5Runtime"] = "1.136.7"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            codes = {item["code"] for item in json.loads(run(VALIDATOR, newer, "--allow-warnings", "--json").stdout)["findings"]}
            self.assertIn("SEMANTIC_UI5_VERSION", codes)

    def test_color_check_ignores_hashes_that_are_not_colors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "interactive").returncode, 0)
            prototype = root / "prototype"
            (prototype / "routes.js").write_text(
                'sap.ui.define([], function () { return { hash: "#/orders/abc", issue: "see #1234" }; });\n',
                encoding="utf-8",
            )
            (prototype / "css" / "ids.css").write_text("#add .face { margin: 0; }\n", encoding="utf-8")
            clean = json.loads(run(VALIDATOR, root, "--allow-warnings", "--json").stdout)
            self.assertNotIn("HARDCODED_COLOR", {item["code"] for item in clean["findings"]})
            (prototype / "css" / "bad.css").write_text(".x { color: #fff; border: 1px solid rgb(0, 0, 0); }\n", encoding="utf-8")
            (prototype / "bad.js").write_text('sap.ui.define([], function () { return "#0a6ed1"; });\n', encoding="utf-8")
            dirty = json.loads(run(VALIDATOR, root, "--allow-warnings", "--json").stdout)
            flagged = {item["path"].replace("\\", "/") for item in dirty["findings"] if item["code"] == "HARDCODED_COLOR"}
            self.assertEqual(flagged, {"prototype/css/bad.css", "prototype/bad.js"})


    # ---- 1.2.0: gate completeness, incremental scaffold, contract-to-UI checks, review mode

    CODE_ARGS = (
        "--app-id", "com.acme.orders", "--name", "Orders", "--language", "en", "--ui5-version", "1.151.0",
        "--service-uri", "/sap/opu/odata4/orders/", "--entity-set", "Orders",
    )

    def findings(self, *arguments: object) -> tuple[int, dict[str, set[str]]]:
        result = run(VALIDATOR, *arguments, "--json")
        by_severity: dict[str, set[str]] = {"error": set(), "warning": set(), "info": set()}
        for item in json.loads(result.stdout)["findings"]:
            by_severity[item["severity"]].add(item["code"])
        return result.returncode, by_severity

    def fill_in(self, contract_path: Path, **target: object) -> dict:
        """Do what a designer has to do before delivery: replace every template value with a real one."""
        def fill(value: object) -> object:
            if isinstance(value, dict):
                return {key: fill(child) for key, child in value.items()}
            if isinstance(value, list):
                return [fill(child) for child in value]
            if isinstance(value, str) and (value.startswith(("Replace", "replace-with", "pending-", "verify-")) or value == "YYYY-MM-DD"):
                return "2026-09-19" if value == "YYYY-MM-DD" else "Decided for this delivery"
            return value

        contract = fill(json.loads(contract_path.read_text(encoding="utf-8")))
        contract["context"]["targetSystem"].update({
            "product": "SAP S/4HANA Cloud", "edition": "public", "release": "2608",
            "fioriGuidelineVersion": "1.148", "launchContext": "standalone", **target,
        })
        contract["dataContract"]["initialSelect"] = ["ID"]
        contract["verification"]["accessibilityEvidence"] = [{"check": "keyboard-only", "method": "manual walkthrough", "result": "passed"}]
        contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
        return contract

    def test_strict_gate_refuses_template_text_and_opens_for_a_completed_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold = run(SCAFFOLD, root, *self.CODE_ARGS, "--output", "code", "--framework", "fiori-elements-odata-v4", "--target-ui5-runtime", "1.152.1")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            code, found = self.findings(root)
            self.assertEqual(code, 1)
            self.assertTrue({"CONTRACT_PLACEHOLDER", "CONTRACT_A11Y_EVIDENCE", "CONTRACT_DATA_BUDGET"} <= found["warning"], found)
            self.fill_in(root / "design-contract.json")
            code, found = self.findings(root)
            self.assertEqual((code, found["error"], found["warning"]), (0, set(), set()), found)

    def test_prototype_delivery_may_not_know_its_target_yet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--language", "en", "--output", "interactive").returncode, 0)
            contract_path = root / "design-contract.json"
            contract = self.fill_in(contract_path)
            contract["context"]["targetSystem"].update({"product": "unknown", "edition": "unknown", "release": "unknown", "fioriGuidelineVersion": "unknown"})
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            code, found = self.findings(root)
            self.assertIn("CONTRACT_TARGET_UNKNOWN", found["info"])
            self.assertEqual((code, found["error"], found["warning"]), (0, set(), set()), found)
            manifest = json.loads((root / "prototype" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["sap.ui5"]["models"]["sample"]["uri"], "model/mockData_en.json")
            self.assertTrue((root / "prototype" / "model" / "mockData_en.json").is_file())

    def test_later_run_adds_code_and_keeps_the_designers_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = ("--app-id", "com.acme.orders", "--name", "Orders", "--language", "en")
            self.assertEqual(run(SCAFFOLD, root, *base, "--output", "interactive").returncode, 0)
            contract_path = root / "design-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["context"]["primaryRole"] = "Internal sales representative"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            marker = root / "prototype" / "view" / "App.view.xml"
            marker.write_text(marker.read_text(encoding="utf-8") + "<!-- designer change -->\n", encoding="utf-8")

            added = run(SCAFFOLD, root, *self.CODE_ARGS, "--output", "all", "--framework", "freestyle-sapui5", "--json")
            self.assertEqual(added.returncode, 0, added.stderr)
            summary = json.loads(added.stdout)
            self.assertEqual((summary["contractMode"], summary["addedTrees"], summary["keptTrees"]), ("kept-and-extended", ["app"], ["prototype"]))
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(contract["context"]["primaryRole"], "Internal sales representative")
            self.assertEqual(contract["project"]["outputs"], ["png", "interactive", "code"])
            self.assertEqual(contract["architecture"]["framework"], "freestyle-sapui5")
            self.assertEqual(contract["dataContract"]["mainService"]["entitySet"], "Orders")
            self.assertEqual(contract["fieldsAndActions"]["actions"][0]["id"], "createButton")
            self.assertIn("designer change", marker.read_text(encoding="utf-8"))
            self.assertTrue((root / "app" / "webapp" / "controller" / "Detail.controller.ts").is_file())

            # --force refreshes scaffold trees, never the contract; only --reset-contract starts it again, with a backup.
            self.assertEqual(run(SCAFFOLD, root, *self.CODE_ARGS, "--output", "all", "--framework", "freestyle-sapui5", "--force").returncode, 0)
            self.assertEqual(json.loads(contract_path.read_text(encoding="utf-8"))["context"]["primaryRole"], "Internal sales representative")
            self.assertNotIn("designer change", marker.read_text(encoding="utf-8"))
            self.assertEqual(run(SCAFFOLD, root, *self.CODE_ARGS, "--output", "all", "--framework", "freestyle-sapui5", "--force", "--reset-contract").returncode, 0)
            self.assertNotEqual(json.loads(contract_path.read_text(encoding="utf-8"))["context"]["primaryRole"], "Internal sales representative")
            self.assertIn("Internal sales representative", (root / "design-contract.json.bak").read_text(encoding="utf-8"))
            other = run(SCAFFOLD, root, "--app-id", "com.other.app", "--name", "Other", "--output", "interactive")
            self.assertEqual(other.returncode, 2)
            self.assertIn("already belongs to", other.stderr)

    def test_contract_texts_and_actions_must_exist_in_the_delivered_ui(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--language", "en", "--output", "interactive").returncode, 0)
            _, found = self.findings(root, "--allow-warnings")
            self.assertFalse({"SEMANTIC_I18N_KEY", "SEMANTIC_ACTION_ID", "SEMANTIC_STATES"} & found["warning"], found)
            contract_path = root / "design-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["fieldsAndActions"]["actions"].append({"id": "approveButton", "labelKey": "approveButtonText", "scope": "table"})
            contract["states"].append({"id": "read-only"})
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            _, found = self.findings(root, "--allow-warnings")
            self.assertTrue({"SEMANTIC_I18N_KEY", "SEMANTIC_ACTION_ID", "SEMANTIC_STATES"} <= found["warning"], found)
            contract["context"]["evidence"][0]["status"] = "probably"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            code, found = self.findings(root, "--allow-warnings")
            self.assertEqual(code, 1)
            self.assertIn("SCHEMA_ENUM", found["error"])

    def test_launchpad_intent_and_search_capability_are_checked_against_the_app(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            without = root / "without"
            self.assertEqual(run(SCAFFOLD, without, *self.CODE_ARGS, "--output", "code", "--framework", "freestyle-sapui5").returncode, 0)
            _, found = self.findings(without, "--allow-warnings")
            self.assertTrue({"SEMANTIC_FLP_INBOUND", "SEMANTIC_SEARCH_UNVERIFIED"} <= found["warning"], found)

            intent = root / "intent"
            scaffold = run(SCAFFOLD, intent, *self.CODE_ARGS, "--output", "code", "--framework", "freestyle-sapui5", "--semantic-object", "SalesOrder", "--action", "manage")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            manifest = json.loads((intent / "app" / "webapp" / "manifest.json").read_text(encoding="utf-8"))
            inbound = manifest["sap.app"]["crossNavigation"]["inbounds"]["SalesOrder-manage"]
            self.assertEqual((inbound["semanticObject"], inbound["action"]), ("SalesOrder", "manage"))
            self.assertEqual(manifest["sap.ui5"]["routing"]["config"]["bypassed"], {"target": "notFound"})
            contract_path = intent / "design-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(contract["context"]["targetSystem"]["launchIntent"], {"semanticObject": "SalesOrder", "action": "manage"})
            contract["dataContract"]["serverCapabilities"]["search"] = True
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            _, found = self.findings(intent, "--allow-warnings")
            self.assertFalse({"SEMANTIC_FLP_INBOUND", "SEMANTIC_SEARCH_UNVERIFIED"} & found["warning"], found)

    def test_png_captures_are_named_after_the_contract(self) -> None:
        png = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (1280).to_bytes(4, "big") + (800).to_bytes(4, "big") + b"\x08\x06\x00\x00\x00"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(run(SCAFFOLD, root, "--app-id", "com.acme.app", "--name", "App", "--output", "png").returncode, 0)
            (root / "visuals" / "sales-order-list-populated-L-horizon-compact.png").write_bytes(png)
            (root / "visuals" / "sales-order-object-no-auth-S-horizon_dark-cozy.png").write_bytes(png)
            _, found = self.findings(root, "--allow-warnings")
            self.assertNotIn("PNG_NAME", found["warning"])
            (root / "visuals" / "screenshot1.png").write_bytes(png)
            (root / "visuals" / "sales-order-list-archived-L-horizon-compact.png").write_bytes(png)
            result = json.loads(run(VALIDATOR, root, "--allow-warnings", "--json").stdout)
            named = sorted(Path(item["path"]).name for item in result["findings"] if item["code"] == "PNG_NAME")
            self.assertEqual(named, ["sales-order-list-archived-L-horizon-compact.png", "screenshot1.png"])

    def test_review_mode_reads_a_project_that_has_no_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(run(SCAFFOLD, root, *self.CODE_ARGS, "--output", "code", "--framework", "freestyle-sapui5").returncode, 0)
            project = root / "app"
            clean = json.loads(run(VALIDATOR, project, "--review", "--json").stdout)
            self.assertEqual((clean["policy"], clean["passed"]), ("review", True), clean["findings"])
            self.assertNotIn("CONTRACT_MISSING", {item["code"] for item in clean["findings"]})
            legacy = project / "webapp" / "controller" / "Legacy.controller.js"
            legacy.write_text('sap.ui.define([], function () {\n  return sap.ui.getCore().byId("x");\n});\n', encoding="utf-8")
            result = run(VALIDATOR, project, "--review", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            finding = next(item for item in report["findings"] if item["code"] == "LEGACY_CORE")
            self.assertEqual((Path(finding["path"]).name, finding["line"]), ("Legacy.controller.js", 2))

    def test_inspector_maps_annotations_to_fields_and_reads_other_entity_kinds(self) -> None:
        module = self.load_inspector()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "abap"
            self.create_rap_package(package)
            (package / "z_c_order.ddls.asddls").write_text("""@Search.searchable: true
define root view entity Z_C_Order as projection on Z_I_Order {
      @UI.lineItem: [{ position: 10 }]
      @UI.selectionField: [{ position: 10 }]
  key OrderId,
      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_Customer', element: 'Customer' } }]
      CustomerId,
      @Semantics.amount.currencyCode: 'Currency'
      Amount,
      Currency
}
""", encoding="utf-8")
            (package / "z_c_order.ddlx.asddlxs").write_text("""@Metadata.layer: #CORE
annotate entity Z_C_Order with {
  @UI.lineItem: [{ position: 20 }]
  @UI.hidden: true
  Amount;
  @UI.identification: [{ position: 10 }]
  OrderId;
}
""", encoding="utf-8")
            (package / "z_a_copy.ddls.asddls").write_text("define abstract entity Z_A_Copy { TargetId : abap.char(10); Quantity : abap.dec(13,3); }", encoding="utf-8")
            (package / "z_ce_stock.ddls.asddls").write_text(
                "@ObjectModel.query.implementedBy: 'ABAP:ZCL_STOCK'\ndefine custom entity Z_CE_Stock { key Plant : werks_d; @UI.lineItem: [{ position: 10 }] Stock : abap.dec(13,3); }",
                encoding="utf-8",
            )
            (package / "z_api_order.srvd.srvdsrv").write_text("define service Z_API_ORDER { expose Z_C_Order as Order; }", encoding="utf-8")
            (package / "z_ui_order_o4.srvb.xml").write_text(
                '<srvb:serviceBinding><srvb:binding srvb:type="ODATA" srvb:version="V4"/>'
                '<srvb:services><srvb:content><srvb:serviceDefinition adtcore:name="Z_UI_ORDER"/></srvb:content></srvb:services></srvb:serviceBinding>',
                encoding="utf-8",
            )
            output = root / "backend.json"
            result = run(INSPECTOR, package, "--output", output, "--service-uri", "/sap/opu/odata4/z_ui_order/")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            semantics = payload["uiSemantics"]
            self.assertEqual(semantics["lineItemFields"], ["Z_C_Order.OrderId", "Z_C_Order.Amount", "Z_CE_Stock.Stock"])
            self.assertEqual(semantics["selectionFields"], ["Z_C_Order.OrderId"])
            self.assertEqual(semantics["valueHelpFields"], ["Z_C_Order.CustomerId"])
            self.assertEqual(semantics["hiddenFields"], ["Z_C_Order.Amount"])
            self.assertEqual(semantics["amountFields"], ["Z_C_Order.Amount"])
            self.assertEqual(semantics["searchableEntities"], ["Z_C_Order"])
            kinds = {item["name"]: (item["kind"], item["fields"], item["keys"]) for item in payload["model"]["entities"]}
            self.assertEqual(kinds["Z_A_Copy"], ("abstract-entity", ["TargetId", "Quantity"], []))
            self.assertEqual(kinds["Z_CE_Stock"], ("custom-entity", ["Plant", "Stock"], ["Plant"]))
            # Two service definitions, but the only readable binding names one of them.
            self.assertEqual((payload["service"]["definition"], payload["service"]["entitySet"]), ("Z_UI_ORDER", "Orders"))
            self.assertEqual(payload["service"]["bindings"][0]["serviceDefinition"], "Z_UI_ORDER")
            self.assertFalse(payload["source"]["inventoryVerified"])
            self.assertTrue(payload["notes"])

            delivery = root / "delivery"
            self.assertEqual(run(SCAFFOLD, delivery, "--app-id", "com.acme.orders", "--name", "Orders", "--output", "code",
                                 "--ui5-version", "1.151.0", "--framework", "freestyle-sapui5", "--backend-contract", output).returncode, 0)
            contract = json.loads((delivery / "design-contract.json").read_text(encoding="utf-8"))
            self.assertIs(contract["dataContract"]["serverCapabilities"]["search"], True)
            _, found = self.findings(delivery, "--allow-warnings")
            self.assertIn("BACKEND_INVENTORY_UNVERIFIED", found["info"])
            self.assertNotIn("SEMANTIC_SEARCH_UNVERIFIED", found["warning"])

        self.assertEqual(module.entity_header("define view ZV_Classic as select from mara { matnr }")["kind"], "classic-view")

    def test_inspector_rejects_a_zip_bomb(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "bomb.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
                handle.writestr("z_c_order.ddls.asddls", "-" * 1_900_000)
            result = run(INSPECTOR, archive, "--output", root / "backend.json")
            self.assertEqual(result.returncode, 2)
            self.assertIn("compression ratio", result.stderr)

    def test_a_profile_without_its_own_lockfile_cannot_scaffold_code(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("scaffold_under_test", SCAFFOLD)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        profiles = {"1.151.0": {"lockfileDir": None}, "1.136.0": {"lockfileDir": None}, "1.120.0": {"lockfileDir": "lockfiles/1.120.0"}}
        template = "ui5-production-freestyle"
        self.assertTrue(module.lockfile_for("1.151.0", profiles, "1.151.0", template).is_file())
        self.assertIsNone(module.lockfile_for("1.136.0", profiles, "1.151.0", template))
        self.assertIsNone(module.lockfile_for("1.120.0", profiles, "1.151.0", template))


if __name__ == "__main__":
    unittest.main()
