/* global fetch */
import 'whatwg-fetch';
import sweetAlert from '../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6'; // eslint-disable-line max-len
import FetchUtil from '../utils/fetchUtil';
import Exception from '../exceptions/exception';
import FetchException from '../exceptions/fetchException';
import DatePicker from './datepicker';

export default class EditUser {
  constructor(link) {
    this.link = link;
    this.modal = document.querySelector(`#${this.link.dataset.modal}`);
    this.type = this.modal.dataset.type;
    this.uid = this.link.dataset.uid;

    this.endpoints = {
      userDetails: '/manage/user/',
      alterHmAttendance: '/attendance/alter/hm/',
      userUpgrade: '/manage/upgrade_user',
    };

    this.render();
  }

  render() {
    this.link.addEventListener('click', (e) => {
      e.preventDefault();

      fetch(this.endpoints.userDetails + this.uid, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
        credentials: 'same-origin',
      })
          .then(FetchUtil.checkStatus)
          .then(FetchUtil.parseJSON)
          .then((data) => {
            this.data = data;

            if (this.type === 'financial') {
              this.renderFinancialModal();
            } else if (this.type === 'freshman') {
              this.renderFreshmanModal();
            } else {
              this.renderModal();
            }
          });
    });
  }

  renderModal() {
    // Clone template modal
    const modal = this.modal.cloneNode(true);
    modal.setAttribute('id',
        `${this.modal.getAttribute('id')}-${this.uid}`);

    // Member Name
    modal.querySelector('input[name=name]').value = this.data.name;
    modal.querySelector('input[name=name]').disabled = true;

    // Room Number
    modal.querySelector('input[name=room]').value = this.data.room_number;

    // On-floor Status
    modal.querySelector('input[name=onfloor]').checked =
        this.data.onfloor_status;

    // Dues
    modal.querySelector('input[name=dues]').checked =
        this.data.active_member;

    // Housing Points
    modal.querySelector('input[name=points]').value = this.data.housing_points;

    // Missed House Meetings
    if (this.data.missed_hm.length > 0) {
      modal.querySelector('.modal-body')
          .removeChild(modal.querySelector('.no-missed-hm-alert'));

      const missedHmTpl = modal.querySelector('.missed-hm-tpl');
      modal.querySelector('.modal-body').removeChild(missedHmTpl);

      this.data.missed_hm.forEach((hm) => {
        const node = missedHmTpl.cloneNode(true);

        node.setAttribute('id', `missedHm-${this.uid}-${hm.id}`);
        node.dataset.id = hm.id;

        node.querySelector('.hm-date').textContent = hm.date;

        if (hm.status === 'Excused') {
          node.querySelector('input[name=hm-excused]').checked = true;
        }

        node.querySelector('input[name=reason]').value = hm.excuse;

        node.querySelector('input[name=hm-excused]').addEventListener(
            'click', e => e.target.classList.add('status-changed') // eslint-disable-line comma-dangle
        );

        node.querySelector('input[name=reason]').addEventListener(
            'input', e => e.target.classList.add('excuse-changed') // eslint-disable-line comma-dangle
        );

        node.querySelector('button').addEventListener('click', (e) => {
          e.preventDefault();
          this.markMissedHmAsPresent(hm.id);
        });

        modal.querySelector('.modal-body').appendChild(node);
      });
    } else {
      modal.querySelector('.modal-body')
          .removeChild(modal.querySelector('.missed-hm-tpl'));
    }

    // Save button
    modal.querySelector('button.save-btn').addEventListener('click', () => {
      this.submitForm(`#${this.modal.getAttribute('id')}-${this.uid}`);
    });

    // Add to DOM and show, then remove on hide
    document.getElementsByTagName('body')[0].appendChild(modal);
    $(`#${this.modal.getAttribute('id')}-${this.uid}`)
        .on('hidden.bs.modal', (e) => {
          document.getElementsByTagName('body')[0].removeChild(e.target);
        })
        .modal('show');
  }

  renderFinancialModal() {
    // Clone template modal
    const modal = this.modal.cloneNode(true);
    modal.setAttribute('id',
        `${this.modal.getAttribute('id')}-${this.uid}`);

    // Member Name
    modal.querySelector('input[name=name]').value = this.data.name;
    modal.querySelector('input[name=name]').disabled = true;

    // Dues
    modal.querySelector('input[name=dues]').checked = this.data.active_member;

    // Save button
    modal.querySelector('button.save-btn').addEventListener('click', () => {
      this.submitForm(`#${this.modal.getAttribute('id')}-${this.uid}`);
    });

    // Add to DOM and show, then remove on hide
    document.getElementsByTagName('body')[0].appendChild(modal);
    $(`#${this.modal.getAttribute('id')}-${this.uid}`)
        .on('hidden.bs.modal', (e) => {
          document.getElementsByTagName('body')[0].removeChild(e.target);
        })
        .modal('show');
  }

  markMissedHmAsPresent(id) {
    FetchUtil.fetchWithWarning(
        `${this.endpoints.alterHmAttendance + this.uid}/${id}`, {
          method: 'GET',
          warningText: 'You will not be able to re-mark this user as absent ' +
          'once they have been marked as present.',
          successText: 'User has been marked as present.',
        }, () => {
          $(`#missedHm-${this.uid}-${id}`).fadeOut();
        } // eslint-disable-line comma-dangle
    );
  }

  renderFreshmanModal() {
    // Clone template modal
    const modal = this.modal.cloneNode(true);
    modal.setAttribute('id',
        `${this.modal.getAttribute('id')}-${this.uid}`);

    // Freshman Name
    modal.querySelector('input[name=name]').value = this.data.name;

    // Room Number
    modal.querySelector('input[name=room]').value = this.data.room_number;

    // On-floor Status
    modal.querySelector('input[name=onfloor]').checked =
        this.data.onfloor_status;

    // Evaluation Date
    modal.querySelector('input[name=evalDate]').value =
        this.data.eval_date;
    new DatePicker(modal.querySelector('input[name=evalDate]'));

    // Freshmen Signatures Missed
    modal.querySelector('input[name=sigMissed]').value =
        this.data.sig_missed;

    // Missed House Meetings
    if (this.data.missed_hm.length > 0) {
      modal.querySelector('.modal-body')
          .removeChild(modal.querySelector('.no-missed-hm-alert'));

      const missedHmTpl = modal.querySelector('.missed-hm-tpl');
      modal.querySelector('.modal-body').removeChild(missedHmTpl);

      this.data.missed_hm.forEach((hm) => {
        const node = missedHmTpl.cloneNode(true);

        node.setAttribute('id', `missedHm-${this.uid}-${hm.id}`);
        node.dataset.id = hm.id;

        node.querySelector('.hm-date').textContent = hm.date;

        if (hm.status === 'Excused') {
          node.querySelector('input[name=hm-excused]').checked = true;
        }

        node.querySelector('input[name=reason]').value = hm.excuse;

        node.querySelector('input[name=hm-excused]').addEventListener(
            'click', e => e.target.classList.add('status-changed') // eslint-disable-line comma-dangle
        );

        node.querySelector('input[name=reason]').addEventListener(
            'input', e => e.target.classList.add('excuse-changed') // eslint-disable-line comma-dangle
        );

        node.querySelector('button').addEventListener('click', (e) => {
          e.preventDefault();
          this.markMissedHmAsPresent(hm.id);
        });

        modal.querySelector('.modal-body').appendChild(node);
      });
    } else {
      modal.querySelector('.modal-body')
          .removeChild(modal.querySelector('.missed-hm-tpl'));
    }

    // Save button
    modal.querySelector('button.save-btn').addEventListener('click', () =>
      this.submitForm() // eslint-disable-line comma-dangle
    );

    // Delete button
    modal.querySelector('button.delete-btn').addEventListener('click', () =>
      this.deleteFreshman() // eslint-disable-line comma-dangle
    );

    // Upgrade button
    modal.querySelector('button.upgrade-btn').addEventListener('click', () =>
      this.upgradeFreshman() // eslint-disable-line comma-dangle
    );

    // Add to DOM and show, then remove on hide
    document.getElementsByTagName('body')[0].appendChild(modal);
    $(`#${this.modal.getAttribute('id')}-${this.uid}`)
        .on('hidden.bs.modal', (e) => {
          document.getElementsByTagName('body')[0].removeChild(e.target);
        })
        .modal('show');
  }

  submitForm() {
    const modal = document.querySelector(`#${this.modal.getAttribute('id')
        }-${this.uid}`);

    modal.querySelectorAll('button').forEach((btn) => {
      btn.disabled = true; // eslint-disable-line no-param-reassign
    });

    if (this.type === 'financial') {
      // Save user details
      const payload = {
        activeMember: modal.querySelector('input[name=dues]').checked,
      };

      FetchUtil.post(this.endpoints.userDetails + this.uid, payload, {
        successText: 'User details have been updated.',
      }, () => {
        $(modal).modal('hide');
      });
    } else {
      // Save missed house meetings
      const missedHms = modal.querySelectorAll('.hm-wrapper');
      missedHms.forEach((hm) => {
        const payload = {
          id: hm.dataset.id,
          status: hm.querySelector('input[name=hm-excused]').checked ?
              'Excused' : 'Absent',
          excuse: hm.querySelector('.hm-reason').value,
        };

        fetch(`${this.endpoints.alterHmAttendance + this.uid
            }/${hm.dataset.id}`, {
              method: 'POST',
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
      });

      // Save user details
      const payload = {
        roomNumber: null,
        onfloorStatus: modal.querySelector('input[name=onfloor]').checked,
      };

      if (this.type === 'member') {
        payload.activeMember = modal.querySelector('input[name=dues]').checked;
        payload.housingPoints = modal.querySelector('input[name=points]').value;
      } else if (this.type === 'freshman') {
        payload.name = modal.querySelector('input[name=name]').value;
        payload.evalDate = modal.querySelector('input[name=evalDate]').value;
        payload.sigMissed = modal.querySelector('input[name=sigMissed]').value;
      }

      const roomNumber = modal.querySelector('input[name=room]').value;
      if (roomNumber && roomNumber !== 'N/A') {
        payload.roomNumber = roomNumber;
      }

      FetchUtil.post(this.endpoints.userDetails + this.uid, payload, {
        successText: 'User details have been updated.',
      }, () => {
        $(modal).modal('hide');
      });
    }
  }

  deleteFreshman() {
    const modal = document.querySelector(`#${this.modal.getAttribute('id')
        }-${this.uid}`);

    FetchUtil.fetchWithWarning(this.endpoints.userDetails + this.uid, {
      method: 'DELETE',
      warningText: "This account's data will be permanently deleted.",
      successText: 'Freshman account has been deleted.',
    }, () => {
      $(modal).modal('hide');
      window.location.reload();
    });
  }

  upgradeFreshman() {
    const modal = document.querySelector(`#${this.modal.getAttribute('id')
        }-${this.uid}`);

    const payload = {
      fid: this.uid,
      uid: modal.querySelector('input[name=upgradeUid]').value,
      sigsMissed: modal.querySelector('input[name=upgradeSigsMissed]').value,
    };

    FetchUtil.postWithWarning(this.endpoints.userUpgrade, payload, {
      warningText: 'This will irreversibly migrate all of this ' +
      "freshman's data to the specified member account.",
      successText: 'Account has been upgraded.',
    }, () => {
      $(modal).modal('hide');
      window.location.reload();
    });
  }
}
