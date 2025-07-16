# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>

from __future__ import annotations

from .hcloud import AnsibleModule


def experimental_warning_function(product: str, url: str):
    """
    Create a reusable experimental warning function.

    Usage:

        product_experimental_warning = experimental_warning_function(
            "Product", "https://docs.hetzner.cloud/changelog#new-product"
        )

        class AnsibleProduct(AnsibleHCloud):
            def __init__(self, module: AnsibleModule):
                product_experimental_warning(module)
                super().__init__(module)

    :param product: Name of the experimental product.
    :param url: Changelog URL announcing the experimental product.
    """
    message = f"Experimental: {product} is experimental, breaking changes may occur within minor releases. See {url} for more details."

    def fn(module: AnsibleModule):
        module.warn(message)

    return fn
