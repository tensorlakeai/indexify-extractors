#!/bin/bash
# Use environment variables to configure your application
echo "Extractor name is $EXTRACTOR_NAME"

# Execute the Docker command
exec "indexify-extractor $@"