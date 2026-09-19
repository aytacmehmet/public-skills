sap.ui.define([
  "sap/ui/Device",
  "sap/ui/core/UIComponent"
], function (Device, UIComponent) {
  "use strict";

  return UIComponent.extend("__APP_ID__.Component", {
    metadata: {
      manifest: "json",
      interfaces: ["sap.ui.core.IAsyncContentCreation"]
    },

    getContentDensityClass: function () {
      return Device.support.touch ? "sapUiSizeCozy" : "sapUiSizeCompact";
    }
  });
});
