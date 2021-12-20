import pytest
from blurg.config import Config
from blurg.diary import DiaryException, DiaryFactory

# We will test in the current directory rather than
# the user's home directory.
CONFIG_BASEDIR = './.blurg_test'
base_url = 'http://localhost:5000'
username = "TESTDIR"


@pytest.fixture(scope="function")
def cfg():
    new_config = Config(basedir=CONFIG_BASEDIR)
    yield new_config
    new_config.delete()


@pytest.fixture(scope="function")
def rem_diary(cfg):
    remote_diary = DiaryFactory.create_remote_diary('test_rem', cfg,
                                                    base_url, username)
    cfg.set_current_diary(diary=remote_diary)
    yield cfg
    remote_diary.delete()


def test_factory_get_diary(cfg):
    diary = DiaryFactory.get_diary('default', cfg)
    assert diary.name == 'default'


def test_diary_delete(cfg):
    # Add a temp diary.
    temp_diary_name = 'to_be_deleted'
    temp_diary = DiaryFactory.get_diary(temp_diary_name, cfg)
    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    local_diary_names = [d.name for d in local_diaries]
    remote_diary_names = [d.name for d in remote_diaries]
    assert temp_diary_name in local_diary_names
    assert temp_diary_name not in remote_diary_names

    # Delete the temp diary and ensure it is gone.
    temp_diary.delete()
    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    local_diary_names = [d.name for d in local_diaries]
    assert temp_diary_name not in local_diary_names


def test_diary_add_entry(cfg):
    diary = cfg.get_current_diary()

    diary.add_entry('Text 1')
    entries = diary.get_entries()
    assert len(entries) == 1 and entries[0].text.strip() == 'Text 1'

    diary.add_entry('Text 2')
    entries = diary.get_entries()
    assert len(entries) == 2


def test_diary_remove_entry(cfg):
    diary = cfg.get_current_diary()
    diary.add_entry('Text 1')
    entries = diary.get_entries()
    assert len(entries) == 1

    the_id = entries[0].id
    diary.remove_entry(the_id)

    entries = diary.get_entries()
    assert len(entries) == 0


def test_diary_remove_entry_fail(cfg):
    bogus_id = 44
    diary = cfg.get_current_diary()
    with pytest.raises(DiaryException):
        diary.remove_entry(bogus_id)

# Remote Diary Tests


def test_factory_create_remote_diary(cfg):
    test_name = 'test'
    user = 'test user'
    remote_diary = DiaryFactory.create_remote_diary(test_name, cfg,
                                                    base_url, user)
    assert remote_diary.name == test_name

    get_rdiary = DiaryFactory.get_diary(test_name, cfg)
    assert get_rdiary.name == test_name


def test_create_local_remote_diary(cfg):
    test_name = 'test'
    user = 'test user'

    remote_diary = DiaryFactory.create_remote_diary(test_name,
                                                    cfg,
                                                    base_url,
                                                    user)

    test_key = remote_diary.get_diarykey()
    cfg.delete_diary(name=test_name)

    remote_diary = DiaryFactory.create_local_remote_diary(test_name,
                                                          test_key,
                                                          user,
                                                          cfg,
                                                          base_url)

    get_rdiary = DiaryFactory.get_diary(test_name, cfg)
    assert get_rdiary.name == test_name


def test_remote_diary_delete(rem_diary):
    # Add a temp diary.
    cfg = rem_diary
    del_diary = DiaryFactory.create_remote_diary('will_delete', cfg,
                                                 base_url, username)
    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    local_diary_names = [d.name for d in local_diaries]
    remote_diary_names = [d.name for d in remote_diaries]
    assert del_diary.name not in local_diary_names
    assert del_diary.name in remote_diary_names

    # Delete the temp diary and ensure it is gone.
    del_diary.delete()
    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    local_diary_names = [d.name for d in local_diaries]
    remote_diary_names = [d.name for d in remote_diaries]
    assert del_diary.name not in local_diary_names
    assert del_diary.name not in remote_diary_names


def test_remote_diary_add_entry(rem_diary):
    cfg = rem_diary
    diary = cfg.get_current_diary()

    diary.add_entry('Text 1')
    entries = diary.get_entries()
    assert len(entries) == 1 and entries[0].text.strip() == 'Text 1'

    diary.add_entry('Text 2')
    entries = diary.get_entries()
    assert len(entries) == 2


def test_remote_diary_remove_entry(rem_diary):
    cfg = rem_diary
    diary = cfg.get_current_diary()
    diary.add_entry('Text 1')
    entries = diary.get_entries()
    assert len(entries) == 1

    the_id = entries[0].id
    diary.remove_entry(the_id)

    entries = diary.get_entries()
    assert len(entries) == 0


def test_remote_diary_remove_entry_fail(rem_diary):
    bogus_id = 44
    cfg = rem_diary
    diary = cfg.get_current_diary()
    with pytest.raises(DiaryException):
        diary.remove_entry(bogus_id)


def test_default_remote_diary(cfg):
    with pytest.raises(DiaryException):
        DiaryFactory.create_remote_diary('default',
                                         cfg,
                                         base_url,
                                         username)


def test_config_remote_diary(cfg):
    with pytest.raises(DiaryException):
        DiaryFactory.create_remote_diary('config',
                                         cfg,
                                         base_url,
                                         username)


def test_same_name_local_remote(cfg):
    local = DiaryFactory.get_diary('local', cfg)
    cfg.set_current_diary(diary=local)
    with pytest.raises(DiaryException):
        DiaryFactory.create_remote_diary('local', cfg, base_url, username)


def test_bad_connection(rem_diary):
    bogus_url = 'http://localhost:9999'
    cfg = rem_diary
    with pytest.raises(DiaryException):
        rem_diary = DiaryFactory.create_remote_diary('test_rem', cfg,
                                                     bogus_url, username)


def test_get_diarykey(rem_diary):
    cfg = rem_diary
    diary = cfg.get_current_diary()
    diarykey = diary.get_diarykey()
    assert diary.params['key'] == diarykey


# Entry Test


def test_entry_date_str(cfg):
    diary = cfg.get_current_diary()

    diary.add_entry('Entry Test')
    entries = diary.get_entries()
    assert entries[0].date.strftime('%m-%d-%Y %H:%M') == entries[0].date_str()
