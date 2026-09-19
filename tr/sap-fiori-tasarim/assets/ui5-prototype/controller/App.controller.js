sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/Filter",
  "sap/ui/model/FilterOperator",
  "sap/ui/model/json/JSONModel",
  "sap/m/MessageBox",
  "sap/m/MessageToast"
], function (Controller, Filter, FilterOperator, JSONModel, MessageBox, MessageToast) {
  "use strict";

  // Open the prototype with ?state=loading|empty|no-results|error|no-auth to demonstrate every designed state.
  const STATES = ["populated", "loading", "empty", "no-results", "error", "no-auth"];

  return Controller.extend("__APP_ID__.controller.App", {
    onInit: function () {
      this.getView().addStyleClass(this.getOwnerComponent().getContentDensityClass());
      this.getView().setModel(new JSONModel({
        state: "populated", tableVisible: true, busy: false, actionsEnabled: true, noDataText: "",
        messageVisible: false, retryVisible: false, illustrationType: "sapIllus-UnableToLoad", messageTitle: "", messageDescription: ""
      }), "ui");
      const requested = new URLSearchParams(window.location.search).get("state");
      this._applyState(STATES.includes(requested) ? requested : "populated");
    },

    _applyState: async function (state) {
      const bundle = await this.getOwnerComponent().getModel("i18n").getResourceBundle();
      const sample = this.getOwnerComponent().getModel("sample");
      const blocked = state === "error" || state === "no-auth";
      this.getView().getModel("ui").setData({
        state: state,
        tableVisible: !blocked,
        busy: state === "loading",
        actionsEnabled: !blocked && state !== "loading",
        noDataText: bundle.getText(state === "empty" ? "emptyText" : "noDataText"),
        messageVisible: blocked,
        retryVisible: state === "error",
        illustrationType: "sapIllus-UnableToLoad",
        messageTitle: blocked ? bundle.getText(state === "error" ? "errorTitle" : "noAuthTitle") : "",
        messageDescription: blocked ? bundle.getText(state === "error" ? "errorDescription" : "noAuthDescription") : ""
      });
      if (state !== "populated") {
        await sample.dataLoaded();
        sample.setProperty("/items", []);
      }
    },

    onSearch: function (event) {
      const query = event.getParameter("newValue");
      const binding = this.byId("itemsTable").getBinding("items");
      const filters = query ? [new Filter({
        filters: [
          new Filter("id", FilterOperator.Contains, query),
          new Filter("name", FilterOperator.Contains, query),
          new Filter("owner", FilterOperator.Contains, query)
        ],
        and: false
      })] : [];
      binding.filter(filters);
    },

    onCreate: async function () {
      if (!this._createDialog) {
        this._createDialog = this.loadFragment({ name: "__APP_ID__.view.CreateDialog" });
      }
      const dialog = await this._createDialog;
      dialog.setModel(new JSONModel({ id: "", name: "", idState: "None", nameState: "None" }), "create");
      dialog.open();
    },

    onCreateInputChange: function (event) {
      const input = event.getSource();
      const property = input.getBinding("value").getPath() + "State";
      input.getModel("create").setProperty(property, event.getParameter("value").trim() ? "None" : "Error");
    },

    onCreateSave: async function () {
      const dialog = await this._createDialog;
      const create = dialog.getModel("create");
      const id = create.getProperty("/id").trim();
      const name = create.getProperty("/name").trim();
      create.setProperty("/idState", id ? "None" : "Error");
      create.setProperty("/nameState", name ? "None" : "Error");
      if (!id || !name) {
        this.byId(id ? "newItemName" : "newItemId").focus();
        return;
      }
      const bundle = await this.getOwnerComponent().getModel("i18n").getResourceBundle();
      const sample = this.getOwnerComponent().getModel("sample");
      const items = sample.getProperty("/items").slice();
      items.unshift({
        id: id,
        name: name,
        owner: bundle.getText("currentUserOwner"),
        statusText: bundle.getText("newStatusText"),
        statusState: "Information"
      });
      sample.setProperty("/items", items);
      dialog.close();
      MessageToast.show(bundle.getText("createdMessage"));
    },

    onCreateCancel: async function () {
      (await this._createDialog).close();
    },

    onRefresh: async function () {
      const model = this.getOwnerComponent().getModel("sample");
      const bundle = await this.getOwnerComponent().getModel("i18n").getResourceBundle();
      await this._applyState("loading");
      try {
        await model.loadData("model/mockData___LANGUAGE__.json");
        await this._applyState("populated");
        MessageToast.show(bundle.getText("refreshMessage"));
      } catch (error) {
        await this._applyState("error");
      }
    },

    onItemPress: async function (event) {
      const context = event.getSource().getBindingContext("sample");
      const bundle = await this.getOwnerComponent().getModel("i18n").getResourceBundle();
      MessageBox.information(bundle.getText("itemDetailMessage", [
        context.getProperty("id"), context.getProperty("name"), context.getProperty("owner")
      ]), { title: bundle.getText("itemDetailTitle") });
    }
  });
});
