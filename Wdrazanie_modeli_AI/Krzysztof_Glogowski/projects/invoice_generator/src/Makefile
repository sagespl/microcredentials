n_docs ?= 130
n_valid_docs ?= 20

notebooks_test_data:
	set PYTHONPATH=%cd% && \
	python invoice_generator/pdf_generator.py --n $(n_docs) --path ../../ml_pipelines/data/01_raw/notebooks/train
	set PYTHONPATH=%cd% && \
	python invoice_generator/pdf_to_jpg_converter.py --pdfs-dir ../../ml_pipelines/data/01_raw/notebooks/train --jpgs-dir ../../ml_pipelines/data/05_model_input/notebooks/train

	set PYTHONPATH=%cd% && \
	python invoice_generator/pdf_generator.py --n $(n_valid_docs) --path ../../ml_pipelines/data/01_raw/notebooks/valid
	set PYTHONPATH=%cd% && \
	python invoice_generator/pdf_to_jpg_converter.py --pdfs-dir ../../ml_pipelines/data/01_raw/notebooks/valid --jpgs-dir ../../ml_pipelines/data/05_model_input/notebooks/valid


pipelines_test_data:
	set PYTHONPATH=%cd% && \
	python invoice_generator/pdf_generator.py --n $(n_docs) --path ../../ml_pipelines/data/01_raw/pdf
