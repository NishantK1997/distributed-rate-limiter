from algorithms.fairness_engine import (
    TenantFairnessEngine
)


def test_should_preserve_multi_tenant_fairness():

    fairness_engine = (
        TenantFairnessEngine()
    )

    fairness_engine.register_tenant(

        tenant_id="tenant_a",

        requests_per_second=1000,

        burst_capacity=1000
    )

    fairness_engine.register_tenant(

        tenant_id="tenant_b",

        requests_per_second=100,

        burst_capacity=100
    )

    fairness_engine.register_tenant(

        tenant_id="tenant_c",

        requests_per_second=500,

        burst_capacity=500
    )

    tenant_a_allowed = 0

    for _ in range(2000):

        if fairness_engine.is_request_allowed(
            "tenant_a"
        ):

            tenant_a_allowed += 1

    tenant_b_allowed = 0

    for _ in range(50):

        if fairness_engine.is_request_allowed(
            "tenant_b"
        ):

            tenant_b_allowed += 1

    tenant_c_allowed = 0

    for _ in range(500):

        if fairness_engine.is_request_allowed(
            "tenant_c"
        ):

            tenant_c_allowed += 1

    expected_upper_bound = 1010

    assert (

        tenant_a_allowed

        <=

        expected_upper_bound
    )

    assert (

        tenant_b_allowed

        ==

        50
    )

    assert (

        tenant_c_allowed

        >=

        450
    )
