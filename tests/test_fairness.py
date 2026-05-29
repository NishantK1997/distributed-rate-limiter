import time

import pytest

from algorithms.fairness_engine import (
    TenantFairnessEngine
)


def test_should_isolate_tenant_limits():

    fairness_engine = (
        TenantFairnessEngine()
    )

    fairness_engine.register_tenant(

        tenant_id="tenant_a",

        requests_per_second=1,

        burst_capacity=1
    )

    fairness_engine.register_tenant(

        tenant_id="tenant_b",

        requests_per_second=10,

        burst_capacity=10
    )

    assert (

        fairness_engine
        .is_request_allowed(
            "tenant_a"
        )

        is True
    )

    assert (

        fairness_engine
        .is_request_allowed(
            "tenant_a"
        )

        is False
    )

    assert (

        fairness_engine
        .is_request_allowed(
            "tenant_b"
        )

        is True
    )


def test_should_reject_unknown_tenant():

    fairness_engine = (
        TenantFairnessEngine()
    )

    assert (

        fairness_engine
        .is_request_allowed(
            "missing_tenant"
        )

        is False
    )


def test_should_validate_invalid_capacity():

    fairness_engine = (
        TenantFairnessEngine()
    )

    with pytest.raises(
        ValueError
    ):

        fairness_engine.register_tenant(

            tenant_id="tenant",

            requests_per_second=0,

            burst_capacity=10
        )


def test_should_refill_tokens_after_wait():

    fairness_engine = (
        TenantFairnessEngine()
    )

    fairness_engine.register_tenant(

        tenant_id="tenant_refill",

        requests_per_second=2,

        burst_capacity=1
    )

    assert (

        fairness_engine
        .is_request_allowed(
            "tenant_refill"
        )

        is True
    )

    assert (

        fairness_engine
        .is_request_allowed(
            "tenant_refill"
        )

        is False
    )

    time.sleep(1)

    assert (

        fairness_engine
        .is_request_allowed(
            "tenant_refill"
        )

        is True
    )