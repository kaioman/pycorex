from pycorex.library.core.pycorex_base import pycorex_base

class pycorex_ai(pycorex_base):
    
    """
    pycorex_ai
    """

    def set_authentication(self, _organization, _api_key):
        """
        認証情報を設定する
        
        Args:
            _organization (str): organization
            _api_key (str): APIキー

        """
        return super().set_authentication(_organization, _api_key)