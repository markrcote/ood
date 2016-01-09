#!/bin/sh
celery -A ood worker -l info -B
