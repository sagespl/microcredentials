# web_app
This it the web application powered by FastApi that is used to provide the REST API for the document classification.
  
# Run

**Reminder**:
<br>
Remember to run the pipelines defined in the **ml_pipelines** project to train the model used in this application

You can run the application either by starting Docker containers locally or by deploying it to a local Kubernetes cluster.
Regardless of the option you choose, you must first copy the model state (e.g., the result of supervised_contrastive_learning) to the 'resources' folder.

To copy model state run the following command:

- If you are Window user:
    ```bash
      make model_windows
    ```
- Otherwise:
    ```bash
      make model
    ```

## Docker
- run the following command to start Docker containers locally:
    ```bash
      make docker
    ```
- open *http://localhost:8080/* in any browser, you should see simple GUI to upload and clusterize pdf file.
  
- run the following command to remove created Docker images and Containers:
    ```bash
      make docker_clean_up