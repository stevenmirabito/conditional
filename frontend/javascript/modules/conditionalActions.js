import FetchUtil from '../utils/fetchUtil';

export default class ConditionalActions {
  constructor(actions) {
    this.actions = actions;
    this.id = this.actions.dataset.id;
    this.endpoint = '/conditionals/review';
    this.deleteEndpoint = `/conditionals/delete/${this.id}`;
    this.render();
  }

  render() {
    this.actions.querySelectorAll('button').forEach((btn) => {
      btn.addEventListener('click', e => this.handleAction(e));
    });
  }

  handleAction(e) {
    const action = e.target.dataset.action;

    if (action === 'delete') {
      FetchUtil.fetchWithWarning(this.deleteEndpoint, {
        method: 'DELETE',
        warningText: 'Are you sure you want to delete this conditional?',
        successText: 'The conditional has been deleted.',
      }, () => {
        $(e.target.closest('tr')).hide();
      });
    } else {
      const actionExt = (action === 'pass') ? 'Passed' : 'Failed';
      const payload = {
        id: this.id,
        status: actionExt,
      };

      FetchUtil.postWithWarning(this.endpoint, payload, {
        warningText: `Are you sure you want to ${action
          } this conditional?`,
        successText: `The conditional has been marked as ${
          actionExt.toLowerCase()}.`,
      });
    }
  }
}
