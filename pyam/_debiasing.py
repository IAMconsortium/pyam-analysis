def _compute_bias(df, name, method, axis):
    """Internal implementation for computing bias weights"""
    if method == "count":
        count = df.meta.groupby(axis).count().exclude
        count.name = name
        df.meta = df.meta.join(count, on=axis, how="outer")
    else:
        raise ValueError(f"Unknown method {method} for computing bias weights!")
