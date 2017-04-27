# Lab: Deploy TensorFlow Model to ML Engine

Lab: Training on Cloud ML Engine の続きです。

現時点では beta 版ですが ML Engine には TensorFlow で学習したモデルをデプロイできる機能があるので試してみましょう。

`trainer/task.py` では `gs://${PROJECT_ID}-ml/mnist/{JOB_NAME}/model/` 以下に学習済みのモデルを保存しています。

## デプロイの手順

```sh
gcloud ml-engine models create mnist --regions us-central1
gcloud ml-engine versions create v1 --model mnist --origin gs://${PROJECT_ID}-ml/mnist/${JOB_NAME}/model
```

## モデルを使ってみる

```sh
gcloud ml-engine predict --model=mnist --json-instances=sample.json
```