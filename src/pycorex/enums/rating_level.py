from enum import IntEnum

class RatingLevel(IntEnum):
        """
        Ratingレベルの列挙体
        高レベルほどセンシティブな内容を含むプロンプトが生成される可能性がある
        """
        
        SAFE = 1
        """ 健全な内容 """

        EMOTIVE = 2
        """ 少しだけ情緒的(フェティッシュなニュアンス) """

        QUESTIONABLE = 3
        """ 下着露出、胸チラなどのギリギリの内容 """

        EXPLICIT = 4
        """ ハードコア一歩手前 """

        LIMITLESS = 5
        """ 制限なし。ナイトメアレベル """