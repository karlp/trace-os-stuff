## freertos task usage via SWO monitoring

Uses libswo from http://git.zapb.de/libswo.git/tree/

Expects to have a freertos trace macro along the lines of

```
/* in your freertosconfig.h */
#define traceTASK_SWITCHED_IN() frt_enter()


/* elsewhere */
#define STIM 31
static inline int get_tid(void) {
	return xTaskGetApplicationTaskTagFromISR(NULL);
}
static volatile uint32_t last_enter;

void frt_enter(void)
{
	uint32_t x = (get_tid() & 0xff) << 24;
	uint32_t prev = last_enter;
	last_enter = DWT_CYCCNT;
	x |= ((last_enter - prev) & 0xffffff);
	trace_send32(STIM, x);
}


/* in your task setup */
	xTaskCreate(task_1, "profilign", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 2, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);
	xTaskCreate(task_2, "is_rad", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 1, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);
	xTaskCreate(task_3, "everybody", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 1, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);
	xTaskCreate(task_4, "should_use_it", configMINIMAL_STACK_SIZE, &state, tskIDLE_PRIORITY + 1, &xHandle);
	vTaskSetApplicationTaskTag(xHandle, ++threadid);

```

## Example output
```
monitoring saw 5
total time: 1071014386 recent time: 29087019
Task<0>(cnt:    1928/  111	avg: 333653.40	ravg: 199798.68) occupied recent: 76.25% all time: 60.06%
Task<1>(cnt:     335/   10	avg:1067074.50	ravg: 678340.10) occupied recent: 23.32% all time: 33.38%
Task<3>(cnt:      33/    0	avg:1042972.76	ravg:      0.00) occupied recent:  0.00% all time:  3.21%
Task<2>(cnt:      66/    1	avg: 520212.89	ravg: 125965.00) occupied recent:  0.43% all time:  3.21%
Task<4>(cnt:      27/    0	avg:  55870.96	ravg:      0.00) occupied recent:  0.00% all time:  0.14%
monitoring saw 5
total time: 1103297043 recent time: 32282657
Task<0>(cnt:    2052/  124	avg: 325492.93	ravg: 198610.75) occupied recent: 76.29% all time: 60.54%
Task<1>(cnt:     345/   10	avg:1051343.70	ravg: 524361.80) occupied recent: 16.24% all time: 32.88%
Task<3>(cnt:      34/    1	avg:1052938.50	ravg:1381808.00) occupied recent:  4.28% all time:  3.24%
Task<2>(cnt:      68/    2	avg: 520052.19	ravg: 514749.00) occupied recent:  3.19% all time:  3.21%
Task<4>(cnt:      27/    0	avg:  55870.96	ravg:      0.00) occupied recent:  0.00% all time:  0.14%
monitoring saw 5
total time: 1136066929 recent time: 32769886
Task<0>(cnt:    2182/  130	avg: 318108.39	ravg: 201546.25) occupied recent: 79.95% all time: 61.10%
Task<1>(cnt:     355/   10	avg:1037584.03	ravg: 562875.20) occupied recent: 17.18% all time: 32.42%
Task<3>(cnt:      35/    1	avg:1041317.91	ravg: 646218.00) occupied recent:  1.97% all time:  3.21%
Task<2>(cnt:      70/    2	avg: 509392.19	ravg: 146952.00) occupied recent:  0.90% all time:  3.14%
Task<4>(cnt:      27/    0	avg:  55870.96	ravg:      0.00) occupied recent:  0.00% all time:  0.13%
```

