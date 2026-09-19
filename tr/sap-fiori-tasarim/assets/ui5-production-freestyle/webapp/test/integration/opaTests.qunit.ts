import Opa5 from "sap/ui/test/Opa5";
import opaTest from "sap/ui/test/opaQunit";
import Press from "sap/ui/test/actions/Press";
import PropertyStrictEquals from "sap/ui/test/matchers/PropertyStrictEquals";

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

opaTest("a row opens the deep-linkable detail page", function (Given: Opa5, When: Opa5, Then: Opa5) {
  Given.iStartMyUIComponent({ componentConfig: { name: "__APP_ID__" } });
  When.waitFor({
    controlType: "sap.m.ColumnListItem",
    viewName: "__APP_ID__.view.Main",
    actions: new Press(),
    errorMessage: "No row was rendered from the service data"
  });
  Then.waitFor({
    id: "detailTitle",
    viewName: "__APP_ID__.view.Detail",
    matchers: new PropertyStrictEquals({ name: "text", value: "1001" }),
    success: function () {
      Opa5.assert.ok(Opa5.getHashChanger().getHash().startsWith("items/"), "The key travels in the hash");
    }
  });
  Then.iTeardownMyApp();
});

opaTest("an unknown address shows the not-found page", function (Given: Opa5, _When: Opa5, Then: Opa5) {
  Given.iStartMyUIComponent({ componentConfig: { name: "__APP_ID__" }, hash: "no/such/page" });
  Then.waitFor({
    id: "notFoundMessage",
    viewName: "__APP_ID__.view.NotFound",
    success: function () {
      Opa5.assert.ok(true, "The bypassed target is displayed");
    }
  });
  Then.iTeardownMyApp();
});
