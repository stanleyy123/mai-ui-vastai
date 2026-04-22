from vastai import Worker, WorkerConfig, HandlerConfig

worker_config = WorkerConfig(
    model_server_url="http://127.0.0.1",
    model_server_port=8080,
    model_healthcheck_url="/health",
    handlers=[
        HandlerConfig(
            route="/ground",
            allow_parallel_requests=False,
            max_queue_time=120.0,
            workload_calculator=lambda payload: 1.0,
        ),
        HandlerConfig(
            route="/health",
            allow_parallel_requests=True,
            workload_calculator=lambda payload: 0.0,
        ),
    ],
)

Worker(worker_config).run()
