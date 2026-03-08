#!/bin/bash
uvicorn glynn_cleaner.api:app --host 0.0.0.0 --port $PORT
