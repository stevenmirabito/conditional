import reveal from 'reveal.js';
import FetchUtil from '../utils/fetchUtil';

export default class ConditionalForm {
  constructor(form) {
    this.form = form;
    this.endpoint = '/conditionals/create';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
            .addEventListener('click', e => this.submitForm(e));
  }

  submitForm(e) {
    e.preventDefault();
    const uid = this.form.uid.value;
    let evaluation = null;
    if (location.pathname.split('/')[1] === 'slideshow') {
      evaluation = location.pathname.split('/')[2];
    }
    const payload = {
      uid,
      description: this.form.querySelector('input[name=description]').value,
      dueDate: this.form.querySelector('input[name=due_date]').value,
      evaluation,
    };
    FetchUtil.postWithWarning(this.endpoint, payload, {
      warningText: 'Are you sure you want to create this conditional?',
      successText: 'The conditional has been created.',
    }, () => {
      $(this.form.closest('.modal')).modal('hide');
      if (location.pathname.split('/')[1] === 'slideshow') {
        $('#createConditional').on('hidden.bs.modal', () => {
          const condBtn = $(`div[data-uid="${uid}"] button`)
          .first();
          $(condBtn).text('Conditionaled').off('click').addClass('disabled');
          $(condBtn).next().hide();
        });
        reveal.right();
      } else {
        location.reload();
      }
    });
  }
}
