from flask import jsonify


def R_ok(msg='操作成功', data=None):
    result = {'code': 0, 'msg': msg}
    if data is not None:
        result['data'] = data
    return jsonify(result)


def R_error(msg='操作失败'):
    return jsonify({'code': 500, 'msg': msg})
