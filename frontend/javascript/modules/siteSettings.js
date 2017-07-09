/* global fetch */
import 'whatwg-fetch';
import sweetAlert from '../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6'; // eslint-disable-line max-len
import FetchUtil from '../utils/fetchUtil';
import Exception from '../exceptions/exception';
import FetchException from '../exceptions/fetchException';

export default class SiteSettings {
  constructor(toggle) {
    this.toggle = toggle;
    this.setting = this.toggle.dataset.setting;

    this.endpoint = '/manage/settings';

    this.render();
  }

  render() {
    this.toggle.addEventListener('click', () => {
      this.updateSetting();
    });
  }

  updateSetting() {
    const payload = {};
    payload[this.setting] = this.toggle.checked;

    fetch(this.endpoint, {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
    })
        .then(FetchUtil.checkStatus)
        .then(FetchUtil.parseJSON)
        .then((response) => {
          if (!response.success) {
            sweetAlert('Uh oh...', "We're having trouble submitting this " +
                'form right now. Please try again later.', 'error');
            throw new Exception(FetchException.REQUEST_FAILED, response);
          }
        })
        .catch((error) => {
          sweetAlert('Uh oh...', "We're having trouble submitting this " +
              'form right now. Please try again later.', 'error');
          throw new Exception(FetchException.REQUEST_FAILED, error);
        });
  }
}
