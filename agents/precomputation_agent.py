import pandas as pd

class PrecomputationAgent:
    def __init__(self, input_path: str, output_path: str = None):
        self.input_path = input_path
        self.output_path = output_path or "Data/Ambi mall Data - Precomputed.xlsx"
        self.df = None

    def load_and_pivot(self):
        df = pd.read_excel(self.input_path)
        df.columns = df.columns.str.strip()
        
        pivot_df = df.pivot_table(
            index='Date',
            columns='KPI Name',
            values='Actual',
            aggfunc='first'
        ).reset_index()

        column_rename_map = {
            "Basket Builder Availabilty": "basket_builder_availability",
            "Availability": "availability",
            "JioMart Delivery SLA Adherence": "jiomart_sla_adherence",
            "Number of Bills": "number_of_bills",
            "Average Bill Value": "average_bill_value",
            "Net Sales": "net_sales",
            "Sales Promotion & Advertisement Cost": "promotion_cost",
            "Customer Complaints Resolved - Offline": "complaints_resolved_offline"
        }
        pivot_df.rename(columns=column_rename_map, inplace=True)

        pivot_df['Date'] = pd.to_datetime(pivot_df['Date'])
        pivot_df.sort_values(by='Date', inplace=True)
        self.df = pivot_df

    def compute_kpis(self):
        df = self.df

        df['daily_sales'] = df['net_sales'].diff()
        df.loc[df.index[0], 'daily_sales'] = df.loc[df.index[0], 'net_sales']
        df['%change_daily_sales'] = df['daily_sales'].pct_change().fillna(0) * 100

        df['sales_picked_up'] = df['daily_sales'] > df['daily_sales'].shift(1)
        df['sales_dropped'] = df['daily_sales'] < df['daily_sales'].shift(1)
        df['is_highest_sales_day'] = df['daily_sales'] == df['daily_sales'].max()
        df['is_lowest_sales_day'] = df['daily_sales'] == df['daily_sales'].min()

        df['abv_x_nob'] = df['average_bill_value'] * df['number_of_bills']
        df['delta_abv_x_nob'] = df['abv_x_nob'].diff().fillna(0)

        df['3_day_slope_netsales'] = df['net_sales'].diff(3).fillna(0) / 3
        df['7_day_slope_netsales'] = df['net_sales'].diff(7).fillna(0) / 7

        self.df = df.round(2)

    def save_output(self):
        self.df.to_excel(self.output_path, index=False)

    def run(self):
        print("📥 Loading and pivoting Excel...")
        self.load_and_pivot()
        print("📊 Computing KPIs...")
        self.compute_kpis()

        # Force output path to fixed location
        self.output_path = "Data/Ambi mall Data - Precomputed.xlsx"

        print("💾 Saving precomputed output to:", self.output_path)
        self.save_output()
        print(f"✅ Precomputation complete. File saved to {self.output_path}")
# 🔥 Add this block so it runs when executed directly
if __name__ == "__main__":
    agent = PrecomputationAgent(
        input_path="Data/Ambi mall Data.xlsx"
    )
    agent.run()