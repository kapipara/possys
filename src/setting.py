
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'kapi', # DB名を設定
            'USER': 'possys', # DBへ接続するユーザIDを設定
            'PASSWORD': 'mokemoke', # DBへ接続するユーザIDのパスワードを設定
            'HOST': 'localhost',
            'PORT': '8889',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            'TEST': {
                'NAME': 'test_sample'
                }
            }
        }

