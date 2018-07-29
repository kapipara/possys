# possysデータベースの構造
 - データベース名: possys
 - テーブルセット
    - MemberList
        - MemberNum smallInt(4) not NULL Unsigned ZEROFILL
        - Name varchar(255) not NULL
        - Email varchar(255)
        - PASSWORD varchar(64)
        - wallet INT not NULL
        - primary key(DataNum)
    - NFCID
        - DataNum smallInt(4) not NULL Unsigned ZEROFILL
        - MemberNum smallInt(3) not NULL Unsigned ZEROFILL
        - IDm varchar(255) not NULL
        - primary key(DataNum)
        - foreign key(MemberNum) references MemberList(MemberNum)
    - MoneyLog
        - LogNum int(10) not NULL Unsigned ZEROFILL
        - MemberNum char(3) not NULL
        - Date datatime not NULL
        - Money int not NULL
        - primary key(LogNum)
    - ログイン名
        - ID: possys_logic
        - PS: pospos
    - MemberNumはMemberListに対し，外部キー制約をもつ

    
