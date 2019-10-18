## freertos task usage via SWO monitoring

Uses libswo from http://git.zapb.de/libswo.git/tree/

Expects to have a freertos trace macro along the lines of

```
/* in your freertosconfig.h */
#define traceTASK_SWITCHED_IN() frt_enter()
#define traceTASK_SWITCHED_OUT() frt_exit()


/* elsewhere */
#define STIM 31

void frt_enter(void)
{
	last_tid = (int)xTaskGetApplicationTaskTagFromISR(NULL) & 0x1f;
	last_enter = DWT_CYCCNT;
}

void frt_exit(void)
{
	uint32_t delta = DWT_CYCCNT - last_enter;
	uint8_t top = 1<<7 | last_tid;
	trace_send32(STIM, (top << 24) | (delta & 0xffffff));
}

	/* in your task setup, set a task tag with a threadid. you have five bits */
	xTaskCreate(task_1, "profilign", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 2, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);
	xTaskCreate(task_2, "is_rad", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 1, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);
	xTaskCreate(task_3, "everybody", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 1, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);
	xTaskCreate(task_4, "should_use_it", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 1, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);

```

## Example output (with --wallclock option)
Task 0 is the idle task.
Cnt is the count total/since last report.
avg/ravg is the lifetime average length, since last report average.
likewise, % recent is since last report
```
monitoring saw 5
total time: 28.69913403125 recent time: 0.999758
Task<1>(cnt:     575/   20 avg: 0.06ms ravg: 0.06ms) occupied recent:  0.11% all time:  0.11%
Task<0>(cnt:     461/   16 avg:31.33ms ravg:31.16ms) occupied recent: 49.86% all time: 50.32%
Task<2>(cnt:     288/   10 avg: 0.09ms ravg: 0.09ms) occupied recent:  0.09% all time:  0.09%
Task<3>(cnt:     485/   17 avg:29.28ms ravg:29.37ms) occupied recent: 49.94% all time: 49.48%
Task<4>(cnt:      29/    1 avg: 0.02ms ravg: 0.02ms) occupied recent:  0.00% all time:  0.00%
monitoring saw 5
total time: 29.74285353125 recent time: 1.0437195
Task<1>(cnt:     596/   21 avg: 0.06ms ravg: 0.06ms) occupied recent:  0.11% all time:  0.11%
Task<0>(cnt:     477/   16 avg:31.32ms ravg:31.16ms) occupied recent: 47.76% all time: 50.23%
Task<2>(cnt:     298/   10 avg: 0.09ms ravg: 0.09ms) occupied recent:  0.08% all time:  0.09%
Task<3>(cnt:     503/   18 avg:29.31ms ravg:30.17ms) occupied recent: 52.04% all time: 49.57%
Task<4>(cnt:      30/    1 avg: 0.02ms ravg: 0.02ms) occupied recent:  0.00% all time:  0.00%
monitoring saw 5
total time: 30.74261153125 recent time: 0.999758
Task<1>(cnt:     616/   20 avg: 0.06ms ravg: 0.06ms) occupied recent:  0.11% all time:  0.11%
Task<0>(cnt:     493/   16 avg:31.32ms ravg:31.16ms) occupied recent: 49.87% all time: 50.22%
Task<2>(cnt:     308/   10 avg: 0.09ms ravg: 0.09ms) occupied recent:  0.09% all time:  0.09%
Task<3>(cnt:     520/   17 avg:29.31ms ravg:29.36ms) occupied recent: 49.93% all time: 49.58%
Task<4>(cnt:      31/    1 avg: 0.02ms ravg: 0.02ms) occupied recent:  0.00% all time:  0.00%

```

