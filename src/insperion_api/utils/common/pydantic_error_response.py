from insperion_api.utils.common.logger import logger


def build_error_response(exc):
    errors = exc.errors()
    logger.error(f"Validation Error, {errors}")
    # Remove the 'input' key from each error dict if present
    for err in errors:
        if "input" in err:
            err.pop("input")
        if "url" in err:
            err.pop("url")
        if "ctx" in err:
            err.pop("ctx")

    return errors
