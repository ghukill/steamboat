# Setter Architecture

## TODO
  * handle when a Step errors or decides to skip itself, or is skipped from upstream error/skip

## Misc
  * Steps are instantiated before registering in Runner DAG
    * allows a simple Step type to be reused without sharing the instance
  * StepContext is passed to the runner during `.run()`, as it will change between invocations
    * better than affixing to class instance, as could change between `.run()` calls
  * You should always be allowed to do `Step.run()` and get a `StepResult` back:
    * allows for typing on the return
    * allows Step logic to be simple, developers extending this
    * puts responsibility on `Runner` to save as `.result` (scaler) and `.caller_result` (dict)