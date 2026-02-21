def clean_whitespace(df):
    
    #Trim whitespace and remove double spaces in all text columns.
    
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
    return df

def to_proper_case(df):
    for col in df.columns:
        if df[col].dtype == "object" and col != "email":
            df[col] = df[col].astype(str).str.title()
    return df