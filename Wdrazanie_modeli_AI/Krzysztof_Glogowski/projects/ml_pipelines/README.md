[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)

This it the project that consist of the following ML pipelines:

- **data_preprocessing** - a pipeline that converts pdf documents into the sequence of images, which serve as input for the ML model 
- **nn_model_training** - a pipeline for training the ML model
- **nn_model_inference** - a pipeline for predicting the class of the document

# Run pipelines

**Info**:
- All pipelines must be run from the main directory of the **document-classification** project
- **data_preprocessing** must be executed first, as it prepares the input data for other pipelines
- **nn_model_training** pipeline must be executed before **nn_model_inference**


- **data_preprocessing** pipeline
  ```bash
    uv run kedro run --pipeline data_preprocessing
  ```
  *optionally you can change the value of parameters you can find [parameters_data_preprocessing.yml](conf/base/parameters_data_preprocessing.yml)*

- **nn_model_training** pipeline
  ```bash
    uv run kedro run --pipeline nn_model_training
  ```
  *optionally you can change the value of parameters you can find [parameters_nn_model_training.yml](conf/base/nn_model_training.yml) e.g. value of **model.encoder.type** from **rnn** to **avg***

- **nn_model_inference** pipeline
  ```bash
    uv run kedro run --pipeline nn_model_inference --params filepath="path/to/you/file.pdf"
  ```

Alternatively you can run command from [Makefile](Makefile) to test pipelines with example configuration. Available commands:

- execute data_preprocessing pipeline:
    ```bash
      make data_preprocessing
    ```
- execute nn_model_training pipeline:
    ```bash
      make nn_model_training
    ```
- execute inference pipeline for example pdf file:
    ```bash
      make nn_model_inference
    ```

# Run pipelines visualization

Run the following command:
```bash
   uv run kedro viz run 
```