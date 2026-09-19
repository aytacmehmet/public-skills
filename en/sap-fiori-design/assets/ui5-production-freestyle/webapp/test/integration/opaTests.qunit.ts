import Opa5 from "sap/ui/test/Opa5";
import opaTest from "sap/ui/test/opaQunit";

Opa5.extendConfig({ autoWait: true, timeout: 30 });

opaTest("the main page is rendered", function (Given: Opa5, _When: Opa5, Then: Opa5) {
  Given.iStartMyUIComponent({ componentConfig: { name: "__APP_ID__" } });
  Then.waitFor({
    id: "pageTitle",
    viewName: "__APP_ID__.view.Main",
    success: function () {
      Opa5.assert.ok(true, "The main page title is visible");
    }
  });
  Then.iTeardownMyApp();
});
