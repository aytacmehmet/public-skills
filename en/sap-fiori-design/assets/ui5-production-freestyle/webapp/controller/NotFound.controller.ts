import Controller from "sap/ui/core/mvc/Controller";
import UIComponent from "sap/ui/core/UIComponent";

/** @namespace __APP_ID__.controller */
export default class NotFound extends Controller {
  public onNavBack(): void {
    (this.getOwnerComponent() as UIComponent).getRouter().navTo("main", {}, undefined, true);
  }
}
