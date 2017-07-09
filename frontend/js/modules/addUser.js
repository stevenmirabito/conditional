import FetchUtil from '../utils/fetchUtil';

export default class AddUser {
  constructor(form) {
    this.form = form;
    this.endpoint = '/manage/user';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
      .addEventListener('click', e => this.submitForm(e));
  }

  submitForm(e) {
    e.preventDefault();

    const payload = {
      name: this.form.querySelector('input[name=name]').value,
      onfloor: this.form.querySelector('input[name=onfloor]').checked,
      roomNumber: this.form.querySelector('input[name=room]').value,
    };

    FetchUtil.post(this.endpoint, payload, {
      successText: 'User has been created.',
    });
  }
}
