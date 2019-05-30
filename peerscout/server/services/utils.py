def filter_by(df, col_name, values):
    return df[df[col_name].isin(values)]
