import Controller from "sap/ui/core/mvc/Controller";
import UIComponent from "sap/ui/core/UIComponent";
import { Route$PatternMatchedEvent } from "sap/ui/core/routing/Route";
import { contextTitle } from "../model/formatter";

// The route carries only the key predicate, for example ('1001'); anything else is not a key of this entity set.
const KEY_PREDICATE = /^\([^/()]*\)$/;

/** @namespace __APP_ID__.controller */
export default class Detail extends Controller {
  public onInit(): void {
    this.getRouter().getRoute("detail")?.attachPatternMatched(this.onPatternMatched, this);
  }

  public formatItemTitle(value: unknown): string {
    return contextTitle(value);
  }

  public onNavBack(): void {
    this.getRouter().navTo("main", {}, undefined, true);
  }

  private onPatternMatched(event: Route$PatternMatchedEvent): void {
    const parameters = event.getParameter("arguments") as { key?: string };
    const key = decodeURIComponent(parameters.key ?? "");
    if (!KEY_PREDICATE.test(key)) {
      this.getRouter().getTargets()?.display("notFound");
      return;
    }
    this.getView()?.bindElement({ path: `/__ENTITY_SET__${key}` });
  }

  private getRouter() {
    return (this.getOwnerComponent() as UIComponent).getRouter();
  }
}
