import pytest
from blurg.config import Config, ConfigException
from blurg.diary import LocalDiary, DiaryFactory

# We will test in the current directory rather than
# the user's home directory.
CONFIG_BASEDIR = './.blurg_test'
TEST_DIARY_NAME = 'test_diary'
base_url = 'http://localhost:5000'
username = "TESTDIR"


@pytest.fixture(scope="function")
def default_cfg():
    new_config = Config(basedir=CONFIG_BASEDIR)
    yield new_config
    new_config.delete()


@pytest.fixture(scope="function")
def cfg():
    new_config = Config(basedir=CONFIG_BASEDIR)
    new_config.set_current_diary(name=TEST_DIARY_NAME)
    yield new_config
    new_config.delete()


def test_check_invalid():
    temp_config = Config(basedir=CONFIG_BASEDIR)
    temp_config.delete()
    with pytest.raises(ConfigException):
        temp_config.check_invalid()


def test_get_current_diary(cfg):
    assert TEST_DIARY_NAME == cfg.get_current_diary().name


def test_set_current_diary(cfg):
    diary2_name = 'test_diary2'
    diary2 = LocalDiary(diary2_name, cfg.basepath)
    diary3_name = 'test_diary3'

    cfg.set_current_diary(diary=diary2)
    assert diary2 == cfg.get_current_diary()
    assert 'test_diary2' == cfg.get_current_diary().name

    cfg.set_current_diary(name=diary3_name)
    assert diary3_name == cfg.get_current_diary().name


def test_set_current_diary_fail(cfg):
    forbidden_diary_name = 'config'
    with pytest.raises(ConfigException):
        cfg.set_current_diary(name=forbidden_diary_name)

    with pytest.raises(ConfigException):
        cfg.set_current_diary()


def test_has_diary(cfg):
    assert cfg.has_diary(diary=cfg.get_current_diary())
    assert cfg.has_diary(name=TEST_DIARY_NAME)


def test_has_diary_fail(cfg):
    with pytest.raises(ConfigException):
        cfg.has_diary()


def test_get_diaries(default_cfg):
    diaries = default_cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) == 1

    default_cfg.set_current_diary(name='diary2')
    diaries = default_cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) == 2

    names = [d.name for d in local_diaries]
    assert 'default' in names and 'diary2' in names

    DiaryFactory.create_remote_diary('remote',
                                     default_cfg,
                                     base_url,
                                     username)

    diaries = default_cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) + len(remote_diaries) == 3


def test_delete_diary(cfg):
    diary1 = DiaryFactory.get_diary("temp", cfg)
    diaries = cfg.get_diaries()

    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) + len(remote_diaries) == 3
    cfg.delete_diary(diary=diary1)
    diaries = cfg.get_diaries()

    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) + len(remote_diaries) == 2


def test_delete_diary_from_name(cfg):
    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]

    assert len(local_diaries) + len(remote_diaries) == 2
    cfg.delete_diary(name=TEST_DIARY_NAME)

    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) + len(remote_diaries) == 1


def test_delete_nonexistent_diary_from_name(cfg):
    bogus_name = 'bogus'
    with pytest.raises(ConfigException):
        cfg.delete_diary(name=bogus_name)


def test_delete_fail(cfg):
    config_name = 'config'
    with pytest.raises(ConfigException):
        cfg.delete_diary(name=config_name)

    with pytest.raises(ConfigException):
        cfg.delete_diary()


def test_promote_diary_success(cfg):
    # promote_diary(self, diaryname, url, user)
    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) == 2
    promoteDiary = local_diaries[1]
    promoteDiary.add_entry('Text 1')

    cfg.promote_diary(promoteDiary.name, base_url, username)

    diaries = cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(remote_diaries) == 1
    assert len(remote_diaries[0].get_entries()) == 1
    remote_diaries[0].delete()
    assert remote_diaries[0].name == "test_diary"


def test_promote_diary_fail(default_cfg):
    bogus_name = 'bogus'
    with pytest.raises(ConfigException):
        default_cfg.promote_diary(bogus_name, base_url, username)


def test_promote_diary_remote_fail(cfg):
    DiaryFactory.create_remote_diary('remote',
                                     cfg,
                                     base_url,
                                     username)

    with pytest.raises(ConfigException):
        cfg.promote_diary('remote', base_url, username)


def test_demote_success(default_cfg):
    diaries = default_cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    assert len(local_diaries) == 1

    DiaryFactory.create_remote_diary('remote',
                                     default_cfg,
                                     base_url,
                                     username)

    diaries = default_cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]

    demoteDiary = remote_diaries[0]
    demoteDiary.add_entry('Text 1')

    default_cfg.demote_diary(demoteDiary.name)

    diaries = default_cfg.get_diaries()
    local_diaries = diaries[0]
    remote_diaries = diaries[1]
    names = [d.name for d in local_diaries]
    assert len(local_diaries) == 2
    assert "remote" in names


def test_demote_fail(default_cfg):
    # demote_diary(self, diary_name)
    bogus_name = 'bogus'
    with pytest.raises(ConfigException):
        default_cfg.demote_diary(bogus_name)


def test_demote_fail2(cfg):
    diary = cfg.get_current_diary()
    with pytest. raises(ConfigException):
        cfg.demote_diary(diary.name)


def test_has_remote_file_success(default_cfg):
    diary = DiaryFactory.create_remote_diary('remote',
                                             default_cfg,
                                             base_url,
                                             username)

    assert default_cfg.has_remote_file(name='remote')
    assert default_cfg.has_remote_file(diary=diary, f_name='key')


def test_has_remote_file_fail1(cfg):
    bogus_name = 'bogus'
    assert not cfg.has_remote_file(name=bogus_name)


def test_has_remote_file_fail2(cfg):
    diary = cfg.get_current_diary()
    assert not cfg.has_remote_file(name=TEST_DIARY_NAME)
    with pytest.raises(ConfigException):
        cfg.has_remote_file(diary=diary, f_name='key')
