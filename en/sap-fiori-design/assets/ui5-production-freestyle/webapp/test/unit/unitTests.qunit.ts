import { contextTitle } from "__APP_PATH__/model/formatter";

QUnit.module("formatter");

QUnit.test("selects common semantic title properties", (assert: Assert) => {
  assert.strictEqual(contextTitle({ ID: "1001" }), "1001");
  assert.strictEqual(contextTitle({ Name: "Item" }), "Item");
  assert.strictEqual(contextTitle({}), "—");
});
