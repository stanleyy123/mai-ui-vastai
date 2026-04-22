from vastai import Worker, WorkerConfig, HandlerConfig, BenchmarkConfig

# Minimal 1x1 white PNG used only for the required benchmark probe
_BENCHMARK_IMAGE_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)

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
            benchmark_config=BenchmarkConfig(
                generator=lambda: {
                    "image": _BENCHMARK_IMAGE_B64,
                    "instruction": "find the button",
                    "zoom_in": False,
                },
                runs=2,
                do_warmup=False,
            ),
        ),
        HandlerConfig(
            route="/health",
            allow_parallel_requests=True,
            workload_calculator=lambda payload: 0.0,
        ),
    ],
)

Worker(worker_config).run()
