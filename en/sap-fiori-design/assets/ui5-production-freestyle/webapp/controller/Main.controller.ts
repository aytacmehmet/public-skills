import Controller from "sap/ui/core/mvc/Controller";
import Context from "sap/ui/model/odata/v4/Context";
import ODataListBinding from "sap/ui/model/odata/v4/ODataListBinding";
import Table from "sap/m/Table";
import MessageBox from "sap/m/MessageBox";
import Component from "../Component";
import { contextTitle } from "../model/formatter";

/** @namespace __APP_ID__.controller */
export default class Main extends Controller {
  public onInit(): void {
    this.getView()?.addStyleClass((this.getOwnerComponent() as Component).getContentDensityClass());
  }

  public formatItemTitle(value: unknown): string {
    return contextTitle(value);
  }

  public onSearch(event: { getParameter(name: string): string }): void {
    const query = event.getParameter("query");
    const binding = (this.byId("itemsTable") as Table).getBinding("items") as ODataListBinding;
    binding.changeParameters({ $search: query || undefined });
  }

  public onRefresh(): void {
    const binding = (this.byId("itemsTable") as Table).getBinding("items") as ODataListBinding;
    binding.refresh();
  }

  public onItemPress(event: { getSource(): { getBindingContext(): Context | undefined } }): void {
    const path = event.getSource().getBindingContext()?.getPath();
    if (path) {
      MessageBox.information(path, { title: this.getResourceText("itemDetailTitle") });
    }
  }

  private getResourceText(key: string): string {
    const model = this.getOwnerComponent()?.getModel("i18n");
    return String(model?.getProperty(key) ?? key);
  }
}
