import pandas as pd

def summarize_sales(file_path):
    """
    Summarizes total units sold and revenue per product.
    """
    df = pd.read_csv(file_path)
    summary = df.groupby('Product')[['Units_Sold', 'Revenue']].sum()
    return summary.to_string()

def get_top_product(file_path):
    """
    Returns the product with the highest total revenue.
    """
    df = pd.read_csv(file_path)
    product_sales = df.groupby('Product')['Revenue'].sum()
    top_product = product_sales.idxmax()
    top_revenue = product_sales.max()
    return f"The top-performing product is '{top_product}' with total revenue of ₹{top_revenue}."

def average_sales(file_path):
    """
    Calculates average revenue per unit sold for each product.
    """
    df = pd.read_csv(file_path)
    df['Revenue per Unit'] = df['Revenue'] / df['Units_Sold']
    avg = df.groupby('Product')['Revenue per Unit'].mean()
    return avg.round(2).to_string()

def filter_by_region(file_path, region):
    """
    Filters sales data for a specific region.
    """
    df = pd.read_csv(file_path)
    filtered = df[df['Region'].str.lower() == region.lower()]
    if filtered.empty:
        return f"No data found for region: {region}"
    return filtered.to_string(index=False)

def sales_trend(file_path):
    """
    Analyzes sales trend over time by aggregating revenue by date.
    """
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    trend = df.groupby('Date')['Revenue'].sum().sort_index()
    return trend.to_string()
