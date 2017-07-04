import reveal from 'reveal.js';
import FetchUtil from '../utils/fetchUtil';

export default class Presentation {
  constructor(element) {
    this.element = element;
    if (location.pathname.split('/')[2] === 'intro') {
      this.endpoint = '/slideshow/intro/review';
    } else {
      this.endpoint = '/slideshow/spring/review';
    }
    this.render();
  }

  render() {
    reveal.initialize();

    $('.reveal button.pass').click((passClickEvent) => {
      passClickEvent.preventDefault();

      const passBtn = passClickEvent.target;
      const uid = passBtn.parentElement.dataset.uid; // Ex: ID of 'pass-ram' => 'ram'
      const cn = passBtn.parentElement.dataset.cn;

      const payload = {
        uid,
        status: 'Passed',
      };

      FetchUtil.postWithWarning(this.endpoint, payload, {
        warningText: `Are you sure you want to pass ${cn}?`,
        successText: `${cn} has been marked as passed.`,
      }, () => {
        $(passBtn).text('Passed').off('click').addClass('disabled');
        $(passBtn).next().hide();
        reveal.right();
      });
    });

    $('.reveal button.fail').click((failClickEvent) => {
      const failBtn = failClickEvent.target;
      const uid = failBtn.parentElement.dataset.uid; // Ex: ID of 'pass-ram' => 'ram'
      const cn = failBtn.parentElement.dataset.cn;

      $(failBtn).prev()
        .removeClass('pass')
        .addClass('conditional')
        .text('Conditional')
        .attr('id', `conditional-${uid}`)
        .off('click')
        .click(() => {
          $('#createConditional').modal();
          $('#createConditional input[type="text"]').val('');
          $('#createConditional input[name="uid"]').val(uid);
        });

      $(failBtn).click((e) => {
        e.preventDefault();

        const payload = {
          uid,
          status: 'Failed',
        };

        FetchUtil.postWithWarning(this.endpoint, payload, {
          warningText: `Are you sure you want to fail ${cn}?`,
          successText: `${cn} has been marked as failed.`,
        }, () => {
          $(failBtn).text('Failed').off('click').addClass('disabled');
          $(failBtn).prev().hide();
          reveal.right();
        });
      });
    });
  }
}
