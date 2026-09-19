import type { SuiteConfiguration } from "sap/ui/test/starter/config";

export default {
  name: "__APP_NAME__ test suite",
  defaults: {
    page: "ui5://test-resources/__APP_PATH__/Test.qunit.html?testsuite={suite}&test={name}",
    qunit: { version: 2 },
    ui5: { theme: "sap_horizon" },
    loader: { paths: { "__APP_PATH__": "../" } }
  },
  tests: {
    "unit/unitTests": { title: "Formatter unit tests" },
    "integration/opaTests": { title: "Main page OPA5 journey" }
  }
} satisfies SuiteConfiguration;
