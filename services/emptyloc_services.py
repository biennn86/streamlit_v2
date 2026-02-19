import pandas as pd
from services.helper_services import normalize_data_lower

class EmptyLocation:
    """Lấy empty loc từ df tồn kho hiện tại
        Args:
            df_data hiện tại
            df_masterlocation từ database thông qua analytics_controller
    """
    def __init__(self, df_data: pd.DataFrame, df_masterloc: pd.DataFrame):
        self.df_data = df_data
        self.df_masterloc = normalize_data_lower(df_masterloc)

    def get_empty_location(self) -> pd.DataFrame:
        """ Chỉ lấy cột location của df_data để tiết kiệm bộ nhớ
            Chỉ lấy vị trí trống của type_rack là hr, pf, mk
            df_masterlocation chỉ lấy locaton có giá trị cột is_active=1 là location đang active
        """
        self.df_data = self.df_data['location']
        self.df_masterloc = self.df_masterloc[self.df_masterloc['is_active']==1]

        df_merge = pd.merge(left=self.df_masterloc,
                        right=self.df_data,
                        on='location',
                        how='left',
                        indicator=True)

        mask = pd.Series(True, df_merge.index)
        mask &= df_merge['_merge'].isin(['left_only'])
        mask &= df_merge['location_usage_type'].isin(['hr', 'pf', 'mk'])

        df_merge = df_merge[mask].reset_index(drop=True)
        #Xóa cột _merge được tạo ra bởi indicator=True
        df_merge = df_merge.drop('_merge', axis=1)
        #Đánh lại số thứ tự
        df_merge.index = range(1, len(df_merge)+1)
       
        return df_merge