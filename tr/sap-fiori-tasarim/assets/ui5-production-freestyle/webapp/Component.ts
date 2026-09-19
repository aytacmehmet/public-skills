import Device from "sap/ui/Device";
import UIComponent from "sap/ui/core/UIComponent";

/** @namespace __APP_ID__ */
export default class Component extends UIComponent {
  public static metadata = { manifest: "json", interfaces: ["sap.ui.core.IAsyncContentCreation"] };

  public init(): void {
    super.init();
    this.getRouter().initialize();
  }

  public getContentDensityClass(): string {
    return Device.support.touch ? "sapUiSizeCozy" : "sapUiSizeCompact";
  }
}
