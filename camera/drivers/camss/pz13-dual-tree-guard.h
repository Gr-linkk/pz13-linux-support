/* SPDX-License-Identifier: GPL-2.0-only */
/* Generated exact DT metadata guard. No MMIO, I2C or power calls. */
static int pz13_validate_dual_tree(void)
{
	struct device_node *node;
	struct property *prop;
	int length;
	node = of_find_node_by_path("/");
	if (!node) return -ENODEV;
	prop = of_find_property(node, "model", &length);
	if (!prop || length != 17) goto mismatch;
	{
		static const u8 expected[] = {0x41,0x53,0x55,0x53,0x20,0x50,0x72,0x6f,0x61,0x72,0x74,0x20,0x50,0x5a,0x31,0x33,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pz13,camera-test-layout", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x64,0x75,0x61,0x6c,0x2d,0x76,0x31,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac15000");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "assigned-clock-rates", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x02,0x3c,0x34,0x60};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "assigned-clocks", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x09};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-names", &length);
	if (!prop || length != 24) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x61,0x6d,0x6e,0x6f,0x63,0x5f,0x61,0x78,0x69,0x00,0x63,0x70,0x61,0x73,0x5f,0x61,0x68,0x62,0x00,0x63,0x63,0x69,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clocks", &length);
	if (!prop || length != 24) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x0e,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x09};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 35) goto mismatch;
	{
		static const u8 expected[] = {0x71,0x63,0x6f,0x6d,0x2c,0x78,0x31,0x65,0x38,0x30,0x31,0x30,0x30,0x2d,0x63,0x63,0x69,0x00,0x71,0x63,0x6f,0x6d,0x2c,0x6d,0x73,0x6d,0x38,0x39,0x39,0x36,0x2d,0x63,0x63,0x69,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "interrupts", &length);
	if (!prop || length != 12) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xcc,0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-0", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcb};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-1", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcc};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-names", &length);
	if (!prop || length != 14) goto mismatch;
	{
		static const u8 expected[] = {0x64,0x65,0x66,0x61,0x75,0x6c,0x74,0x00,0x73,0x6c,0x65,0x65,0x70,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domains", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x0a,0xc1,0x50,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "status", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x6f,0x6b,0x61,0x79,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac15000/i2c-bus@0");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-frequency", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x06,0x1a,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac15000/i2c-bus@0/camera@36");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "b5-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd1};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "b7-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd2};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-names", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x6d,0x63,0x6c,0x6b,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clocks", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x47};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 23) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x2c,0x72,0x65,0x61,0x72,0x2d,0x63,0x61,0x70,0x74,0x75,0x72,0x65,0x2d,0x74,0x65,0x73,0x74,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "m2-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcd};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "m4-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xce};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "m5-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcf};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "m6-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd0};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "orientation", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-0", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd3};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-1", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd4};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-names", &length);
	if (!prop || length != 14) goto mismatch;
	{
		static const u8 expected[] = {0x64,0x65,0x66,0x61,0x75,0x6c,0x74,0x00,0x73,0x6c,0x65,0x65,0x70,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domains", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x36};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reset-line-gpios", &length);
	if (!prop || length != 12) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x56,0x00,0x00,0x00,0x6d,0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac15000/i2c-bus@0/camera@36/port");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac15000/i2c-bus@0/camera@36/port/endpoint");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bus-type", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x04};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-lanes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x07};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "data-lanes", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "link-frequencies", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x20,0x2f,0xbf,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd5};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "remote-endpoint", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd6};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac15000/i2c-bus@1");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-frequency", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x06,0x1a,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac16000");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "assigned-clock-rates", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x02,0x3c,0x34,0x60};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "assigned-clocks", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x0b};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-names", &length);
	if (!prop || length != 24) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x61,0x6d,0x6e,0x6f,0x63,0x5f,0x61,0x78,0x69,0x00,0x63,0x70,0x61,0x73,0x5f,0x61,0x68,0x62,0x00,0x63,0x63,0x69,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clocks", &length);
	if (!prop || length != 24) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x0e,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x0b};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 35) goto mismatch;
	{
		static const u8 expected[] = {0x71,0x63,0x6f,0x6d,0x2c,0x78,0x31,0x65,0x38,0x30,0x31,0x30,0x30,0x2d,0x63,0x63,0x69,0x00,0x71,0x63,0x6f,0x6d,0x2c,0x6d,0x73,0x6d,0x38,0x39,0x39,0x36,0x2d,0x63,0x63,0x69,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "interrupts", &length);
	if (!prop || length != 12) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x0f,0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-0", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe2};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-1", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe3};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-names", &length);
	if (!prop || length != 14) goto mismatch;
	{
		static const u8 expected[] = {0x64,0x65,0x66,0x61,0x75,0x6c,0x74,0x00,0x73,0x6c,0x65,0x65,0x70,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domains", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x0a,0xc1,0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "status", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x6f,0x6b,0x61,0x79,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac16000/i2c-bus@0");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-frequency", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x06,0x1a,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac16000/i2c-bus@1");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-frequency", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x06,0x1a,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac16000/i2c-bus@1/camera@36");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "b5-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd1};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-names", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x6d,0x63,0x6c,0x6b,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clocks", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x4f};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 24) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x2c,0x66,0x72,0x6f,0x6e,0x74,0x2d,0x63,0x61,0x70,0x74,0x75,0x72,0x65,0x2d,0x74,0x65,0x73,0x74,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "m3-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe6};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "orientation", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-0", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe4};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-1", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe5};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pinctrl-names", &length);
	if (!prop || length != 14) goto mismatch;
	{
		static const u8 expected[] = {0x64,0x65,0x66,0x61,0x75,0x6c,0x74,0x00,0x73,0x6c,0x65,0x65,0x70,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domains", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-gpios", &length);
	if (!prop || length != 12) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x56,0x00,0x00,0x00,0x06,0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x36};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reset-line-gpios", &length);
	if (!prop || length != 12) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x56,0x00,0x00,0x00,0xed,0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac16000/i2c-bus@1/camera@36/port");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/cci@ac16000/i2c-bus@1/camera@36/port/endpoint");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bus-type", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x04};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-lanes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x07};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "data-lanes", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "link-frequencies", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x1a,0xd2,0x74,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe0};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "remote-endpoint", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe1};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/clock-controller@ade0000");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "#clock-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#power-domain-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#reset-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clocks", &length);
	if (!prop || length != 20) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x33,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x28,0x00,0x00,0x01,0x11,0x00,0x00,0x00,0x29};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 20) goto mismatch;
	{
		static const u8 expected[] = {0x71,0x63,0x6f,0x6d,0x2c,0x78,0x31,0x70,0x34,0x32,0x31,0x30,0x30,0x2d,0x63,0x61,0x6d,0x63,0x63,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domains", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x31,0x00,0x00,0x00,0x0a,0x00,0x00,0x00,0x31,0x00,0x00,0x00,0x06};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x0a,0xde,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "required-opps", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x25,0x00,0x00,0x00,0x25};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/isp@acb7000");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "clock-names", &length);
	if (!prop || length != 243) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x61,0x6d,0x6e,0x6f,0x63,0x5f,0x6e,0x72,0x74,0x5f,0x61,0x78,0x69,0x00,0x63,0x61,0x6d,0x6e,0x6f,0x63,0x5f,0x72,0x74,0x5f,0x61,0x78,0x69,0x00,0x63,0x6f,0x72,0x65,0x5f,0x61,0x68,0x62,0x00,0x63,0x70,0x61,0x73,0x5f,0x61,0x68,0x62,0x00,0x63,0x70,0x61,0x73,0x5f,0x66,0x61,0x73,0x74,0x5f,0x61,0x68,0x62,0x00,0x63,0x70,0x61,0x73,0x5f,0x76,0x66,0x65,0x30,0x00,0x63,0x70,0x61,0x73,0x5f,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x00,0x63,0x73,0x69,0x64,0x00,0x63,0x73,0x69,0x64,0x5f,0x63,0x73,0x69,0x70,0x68,0x79,0x5f,0x72,0x78,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x30,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x30,0x5f,0x74,0x69,0x6d,0x65,0x72,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x34,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x34,0x5f,0x74,0x69,0x6d,0x65,0x72,0x00,0x67,0x63,0x63,0x5f,0x61,0x78,0x69,0x5f,0x68,0x66,0x00,0x67,0x63,0x63,0x5f,0x61,0x78,0x69,0x5f,0x73,0x66,0x00,0x76,0x66,0x65,0x30,0x00,0x76,0x66,0x65,0x30,0x5f,0x66,0x61,0x73,0x74,0x5f,0x61,0x68,0x62,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x5f,0x61,0x68,0x62,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x5f,0x63,0x70,0x68,0x79,0x5f,0x72,0x78,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x5f,0x63,0x73,0x69,0x64,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clocks", &length);
	if (!prop || length != 168) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x04,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x0d,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x0e,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x10,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x11,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x13,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x23,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x25,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x26,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x17,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x2a,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x1f,0x00,0x00,0x00,0x33,0x00,0x00,0x00,0x11,0x00,0x00,0x00,0x33,0x00,0x00,0x00,0x12,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x31,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x34,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x3a,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x39,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x3c,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x3d};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 33) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x2c,0x78,0x31,0x70,0x34,0x32,0x31,0x30,0x30,0x2d,0x64,0x75,0x61,0x6c,0x2d,0x63,0x61,0x70,0x74,0x75,0x72,0x65,0x2d,0x63,0x61,0x6d,0x73,0x73,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "interconnect-names", &length);
	if (!prop || length != 32) goto mismatch;
	{
		static const u8 expected[] = {0x61,0x68,0x62,0x00,0x68,0x66,0x5f,0x6d,0x6e,0x6f,0x63,0x00,0x73,0x66,0x5f,0x6d,0x6e,0x6f,0x63,0x00,0x73,0x66,0x5f,0x69,0x63,0x70,0x5f,0x6d,0x6e,0x6f,0x63,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "interconnects", &length);
	if (!prop || length != 96) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x35,0x00,0x00,0x00,0x03,0x00,0x00,0x00,0x03,0x00,0x00,0x00,0x36,0x00,0x00,0x00,0x05,0x00,0x00,0x00,0x03,0x00,0x00,0x00,0xf8,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x19,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0xf8,0x00,0x00,0x00,0x03,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x19,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0xf8,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x19,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x07};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "interrupt-names", &length);
	if (!prop || length != 81) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x73,0x69,0x64,0x30,0x00,0x63,0x73,0x69,0x64,0x31,0x00,0x63,0x73,0x69,0x64,0x32,0x00,0x63,0x73,0x69,0x64,0x5f,0x6c,0x69,0x74,0x65,0x30,0x00,0x63,0x73,0x69,0x64,0x5f,0x6c,0x69,0x74,0x65,0x31,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x30,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x34,0x00,0x76,0x66,0x65,0x30,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x30,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x31,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "interrupts", &length);
	if (!prop || length != 120) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xd0,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xd2,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xaf,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xd4,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x67,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xdd,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7a,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xd1,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0xd5,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x68,0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "iommus", &length);
	if (!prop || length != 60) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x32,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x60,0x00,0x00,0x00,0x32,0x00,0x00,0x08,0x60,0x00,0x00,0x00,0x60,0x00,0x00,0x00,0x32,0x00,0x00,0x18,0x60,0x00,0x00,0x00,0x60,0x00,0x00,0x00,0x32,0x00,0x00,0x18,0xe0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x32,0x00,0x00,0x19,0xa0,0x00,0x00,0x00,0x20};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domain-names", &length);
	if (!prop || length != 9) goto mismatch;
	{
		static const u8 expected[] = {0x69,0x66,0x65,0x30,0x00,0x74,0x6f,0x70,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "power-domains", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x01,0x00,0x00,0x01,0xc8,0x00,0x00,0x00,0x05};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 224) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x0a,0xcb,0x70,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x0a,0xcb,0x90,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x0a,0xcb,0xb0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x0a,0xcc,0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x00,0x00,0x0a,0xcc,0xa0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x00,0x00,0x0a,0xcb,0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x00,0x00,0x0a,0xce,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x0a,0xce,0xc0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x40,0x00,0x00,0x00,0x00,0x00,0x0a,0xcf,0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x00,0x00,0x0a,0xcf,0x70,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x00,0x00,0x0a,0xcf,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x00,0x00,0x0a,0xc6,0x20,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xf0,0x00,0x00,0x00,0x00,0x00,0x0a,0xcc,0x70,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x0a,0xcc,0xb0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg-names", &length);
	if (!prop || length != 118) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x73,0x69,0x64,0x30,0x00,0x63,0x73,0x69,0x64,0x31,0x00,0x63,0x73,0x69,0x64,0x32,0x00,0x63,0x73,0x69,0x64,0x5f,0x6c,0x69,0x74,0x65,0x30,0x00,0x63,0x73,0x69,0x64,0x5f,0x6c,0x69,0x74,0x65,0x31,0x00,0x63,0x73,0x69,0x64,0x5f,0x77,0x72,0x61,0x70,0x70,0x65,0x72,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x30,0x00,0x63,0x73,0x69,0x70,0x68,0x79,0x34,0x00,0x63,0x73,0x69,0x74,0x70,0x67,0x30,0x00,0x63,0x73,0x69,0x74,0x70,0x67,0x31,0x00,0x63,0x73,0x69,0x74,0x70,0x67,0x32,0x00,0x76,0x66,0x65,0x30,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x30,0x00,0x76,0x66,0x65,0x5f,0x6c,0x69,0x74,0x65,0x31,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "status", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x6f,0x6b,0x61,0x79,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-csiphy-0p8-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc9};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-csiphy-1p2-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xca};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/isp@acb7000/ports");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/isp@acb7000/ports/port@0");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/isp@acb7000/ports/port@0/endpoint");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bus-type", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x04};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-lanes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x07};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "data-lanes", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd6};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "remote-endpoint", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd5};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/isp@acb7000/ports/port@1");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 1) goto mismatch;
	prop = of_find_property(node, "#address-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "#size-cells", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "reg", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/isp@acb7000/ports/port@1/endpoint");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bus-type", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x04};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "clock-lanes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x07};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "data-lanes", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe1};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "remote-endpoint", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe0};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-cci0-default-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-pull-up", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x63,0x69,0x5f,0x69,0x32,0x63,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcb};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x31,0x30,0x31,0x00,0x67,0x70,0x69,0x6f,0x31,0x30,0x32,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-cci0-sleep-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-pull-down", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x63,0x69,0x5f,0x69,0x32,0x63,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcc};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x31,0x30,0x31,0x00,0x67,0x70,0x69,0x6f,0x31,0x30,0x32,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-cci1-default-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-pull-up", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x61,0x6f,0x6e,0x5f,0x63,0x63,0x69,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe2};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x32,0x33,0x35,0x00,0x67,0x70,0x69,0x6f,0x32,0x33,0x36,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-cci1-sleep-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-pull-down", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x61,0x6f,0x6e,0x5f,0x63,0x63,0x69,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe3};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 16) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x32,0x33,0x35,0x00,0x67,0x70,0x69,0x6f,0x32,0x33,0x36,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-active-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 3) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe4};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-active-pins/enable-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "output-low", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 6) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x36,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-active-pins/mclk-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x61,0x6d,0x5f,0x61,0x6f,0x6e,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x31,0x30,0x30,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-active-pins/reset-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "output-low", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x32,0x33,0x37,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-sleep-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe5};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-sleep-pins/control-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "output-low", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 14) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x32,0x33,0x37,0x00,0x67,0x70,0x69,0x6f,0x36,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-front-id-sleep-pins/mclk-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-pull-down", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "input-enable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x31,0x30,0x30,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-rear-id-active-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd3};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-rear-id-active-pins/mclk-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 9) goto mismatch;
	{
		static const u8 expected[] = {0x63,0x61,0x6d,0x5f,0x6d,0x63,0x6c,0x6b,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 7) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x39,0x36,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-rear-id-active-pins/reset-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "output-low", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x31,0x30,0x39,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-rear-id-sleep-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd4};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-rear-id-sleep-pins/mclk-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-pull-down", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "input-enable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 7) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x39,0x36,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/pinctrl@f100000/pz13-rear-id-sleep-pins/reset-pins");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "bias-disable", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "drive-strength", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x02};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "function", &length);
	if (!prop || length != 5) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "output-low", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "pins", &length);
	if (!prop || length != 8) goto mismatch;
	{
		static const u8 expected[] = {0x67,0x70,0x69,0x6f,0x31,0x30,0x39,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8010");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 5) goto mismatch;
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 28) goto mismatch;
	{
		static const u8 expected[] = {0x71,0x63,0x6f,0x6d,0x2c,0x70,0x6d,0x38,0x30,0x31,0x30,0x2d,0x72,0x70,0x6d,0x68,0x2d,0x72,0x65,0x67,0x75,0x6c,0x61,0x74,0x6f,0x72,0x73,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,pmic-id", &length);
	if (!prop || length != 2) goto mismatch;
	{
		static const u8 expected[] = {0x6d,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-l1-l2-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0x8a};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-l3-l4-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0x87};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-l5-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0x88};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-l6-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0x87};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8010/ldo2");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcd};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x12,0x4f,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x12,0x4f,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 18) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x72,0x65,0x61,0x72,0x5f,0x6c,0x32,0x6d,0x5f,0x31,0x70,0x32,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8010/ldo3");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xe6};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x1b,0x77,0x40};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x1b,0x77,0x40};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 19) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x66,0x72,0x6f,0x6e,0x74,0x5f,0x6c,0x33,0x6d,0x5f,0x31,0x70,0x38,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8010/ldo4");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xce};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x1b,0x77,0x40};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x1b,0x77,0x40};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 18) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x72,0x65,0x61,0x72,0x5f,0x6c,0x34,0x6d,0x5f,0x31,0x70,0x38,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8010/ldo5");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xcf};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x2a,0xb9,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x2a,0xb9,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 18) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x72,0x65,0x61,0x72,0x5f,0x6c,0x35,0x6d,0x5f,0x32,0x70,0x38,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8010/ldo6");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd0};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x1b,0x77,0x40};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x1b,0x77,0x40};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 18) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x72,0x65,0x61,0x72,0x5f,0x6c,0x36,0x6d,0x5f,0x31,0x70,0x38,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8550");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 2) goto mismatch;
	prop = of_find_property(node, "compatible", &length);
	if (!prop || length != 28) goto mismatch;
	{
		static const u8 expected[] = {0x71,0x63,0x6f,0x6d,0x2c,0x70,0x6d,0x38,0x35,0x35,0x30,0x2d,0x72,0x70,0x6d,0x68,0x2d,0x72,0x65,0x67,0x75,0x6c,0x61,0x74,0x6f,0x72,0x73,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,pmic-id", &length);
	if (!prop || length != 2) goto mismatch;
	{
		static const u8 expected[] = {0x62,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-l5-l16-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0x88};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "vdd-l6-l7-supply", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0x89};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8550/ldo5");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd1};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x2d,0xc6,0xc0};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x2d,0xc6,0xc0};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 18) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x72,0x65,0x61,0x72,0x5f,0x6c,0x35,0x62,0x5f,0x33,0x70,0x30,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/pz13-rear-pm8550/ldo7");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xd2};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-allowed-modes", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x2a,0xb9,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x2a,0xb9,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 18) goto mismatch;
	{
		static const u8 expected[] = {0x70,0x7a,0x31,0x33,0x5f,0x72,0x65,0x61,0x72,0x5f,0x6c,0x37,0x62,0x5f,0x32,0x70,0x38,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/regulators-1/ldo1");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xca};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-initial-mode", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x12,0x4f,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x12,0x4f,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 13) goto mismatch;
	{
		static const u8 expected[] = {0x76,0x72,0x65,0x67,0x5f,0x6c,0x31,0x63,0x5f,0x31,0x70,0x32,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	node = of_find_node_by_path("/soc@0/rsc@17500000/regulators-1/ldo2");
	if (!node) return -ENODEV;
	if (of_get_child_count(node) != 0) goto mismatch;
	prop = of_find_property(node, "phandle", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x01,0xc9};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "qcom,always-wait-for-ack", &length);
	if (!prop || length != 0) goto mismatch;
	prop = of_find_property(node, "regulator-initial-mode", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x00,0x00,0x03};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-max-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x0d,0x6d,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-min-microvolt", &length);
	if (!prop || length != 4) goto mismatch;
	{
		static const u8 expected[] = {0x00,0x0d,0x6d,0x80};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	prop = of_find_property(node, "regulator-name", &length);
	if (!prop || length != 13) goto mismatch;
	{
		static const u8 expected[] = {0x76,0x72,0x65,0x67,0x5f,0x6c,0x32,0x63,0x5f,0x30,0x70,0x38,0x00};
		if (memcmp(prop->value, expected, sizeof(expected))) goto mismatch;
	}
	of_node_put(node);
	return 0;
mismatch:
	of_node_put(node);
	return -EINVAL;
}
