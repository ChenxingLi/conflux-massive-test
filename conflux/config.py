DEFAULT_PY_TEST_CHAIN_ID = 10

small_local_test_conf = dict(
    chain_id = DEFAULT_PY_TEST_CHAIN_ID,
    check_phase_change_period_ms = 100,
    enable_discovery = "false",
    log_file = "'./conflux.log'",
    log_level = '"debug"',
    metrics_output_file = "'./metrics.log'",
    metrics_enabled = "true",
    mode = '"test"',
    session_ip_limits = "'0,0,0,0'",
    mining_type = "'disable'",
    storage_delta_mpts_cache_size = 200_000,
    storage_delta_mpts_cache_start_size = 200_000,
    storage_delta_mpts_slab_idle_size = 2_000_000,
    subnet_quota = 0,
    persist_tx_index = "true",
    persist_block_number_index = "true",
    execute_genesis = "false",
    dev_allow_phase_change_without_peer = "true",
    check_status_genesis = "false",
    pos_reference_enable_height = 0,
    hydra_transition_height = 0,
    hydra_transition_number = 0,
    cip43_init_end_number = 2 ** 32 - 1,
    min_phase_change_normal_peer_count = 1,
    dao_vote_transition_number = 2**31,
    dao_vote_transition_height = 2**31,
    enable_single_mpt_storage = "true",
    rpc_enable_metrics = "true",
)

default_conflux_conf = dict(
    chain_id = DEFAULT_PY_TEST_CHAIN_ID,
    db_cache_size = 128,
    ledger_cache_size = 1024,
    storage_delta_mpts_cache_size = 20_000_000,
    storage_delta_mpts_cache_start_size = 2_000_000,
    storage_delta_mpts_slab_idle_size = 2_000_000,
    tx_pool_size = 500_000,
    persist_tx_index = "true",
    persist_block_number_index = "true",
)

production_conf = default_conflux_conf