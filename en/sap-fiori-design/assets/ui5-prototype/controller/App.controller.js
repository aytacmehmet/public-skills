sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/Filter",
  "sap/ui/model/FilterOperator",
  "sap/m/Button",
  "sap/m/Dialog",
  "sap/m/Input",
  "sap/m/Label",
  "sap/m/MessageBox",
  "sap/m/MessageToast",
  "sap/m/VBox"
], function (Controller, Filter, FilterOperator, Button, Dialog, Input, Label, MessageBox, MessageToast, VBox) {
  "use strict";

  return Controller.extend("__APP_ID__.controller.App", {
    onInit: function () {
      this.getView().addStyleClass(this.getOwnerComponent().getContentDensityClass());
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
      const bundle = await this.getOwnerComponent().getModel("i18n").getResourceBundle();
      const idInput = new Input(this.createId("newItemId"), { required: true });
      const nameInput = new Input(this.createId("newItemName"), { required: true });
      const dialog = new Dialog(this.createId("createDialog"), {
        title: bundle.getText("createDialogTitle"),
        contentWidth: "26rem",
        content: new VBox({
          items: [
            new Label({ text: bundle.getText("idColumn"), labelFor: idInput }),
            idInput,
            new Label({ text: bundle.getText("nameColumn"), labelFor: nameInput }).addStyleClass("sapUiSmallMarginTop"),
            nameInput
          ]
        }).addStyleClass("sapUiContentPadding"),
        beginButton: new Button({
          text: bundle.getText("saveButtonText"),
          type: "Emphasized",
          press: () => {
            if (!idInput.getValue().trim() || !nameInput.getValue().trim()) {
              MessageBox.error(bundle.getText("requiredFieldsMessage"));
              return;
            }
            const model = this.getOwnerComponent().getModel("sample");
            const items = model.getProperty("/items").slice();
            items.unshift({
              id: idInput.getValue().trim(),
              name: nameInput.getValue().trim(),
              owner: bundle.getText("currentUserOwner"),
              statusText: bundle.getText("newStatusText"),
              statusState: "Information"
            });
            model.setProperty("/items", items);
            dialog.close();
            MessageToast.show(bundle.getText("createdMessage"));
          }
        }),
        endButton: new Button({ text: bundle.getText("cancelButtonText"), press: () => dialog.close() }),
        afterClose: () => dialog.destroy()
      });
      this.getView().addDependent(dialog);
      dialog.open();
    },

    onRefresh: async function () {
      const model = this.getOwnerComponent().getModel("sample");
      const bundle = await this.getOwnerComponent().getModel("i18n").getResourceBundle();
      this.byId("itemsTable").setBusy(true);
      try {
        await model.loadData("model/mockData.json");
        MessageToast.show(bundle.getText("refreshMessage"));
      } catch (error) {
        MessageBox.error(bundle.getText("refreshErrorMessage"));
      } finally {
        this.byId("itemsTable").setBusy(false);
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
