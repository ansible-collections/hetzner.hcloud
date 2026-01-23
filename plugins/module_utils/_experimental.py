# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._base import AnsibleModule


def experimental_warning_function(product: str, maturity: str, url: str):
    """
    Create a reusable experimental warning function.

    Usage:

        product_experimental_warning = experimental_warning_function(
            "Product",
            "in beta",
            "https://docs.hetzner.cloud/changelog#new-product",
        )

        class AnsibleProduct(AnsibleHCloud):
            def __init__(self, module: AnsibleModule):
                product_experimental_warning(module)
                super().__init__(module)

    :param product: Name of the product.
    :param maturity: Maturity of the product.
    :param url: Changelog URL announcing the product.
    """
    message = f"Experimental: {product} is {maturity}, breaking changes may occur within minor releases. See {url} for more details."

    def fn(module: AnsibleModule):
        module.warn(message)

    return fn
