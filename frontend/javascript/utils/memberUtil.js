import _ from 'lodash';

export default class MemberUtil {
  static splitFreshmenUpperclassmen(memberIds) {
    const result = {
      freshmen: [],
      upperclassmen: [],
    };

    memberIds.forEach((memberId) => {
      if (memberId) {
        if (_.isNaN(_.toNumber(memberId))) {
          // Upperclassman account
          result.upperclassmen.push(memberId);
        } else {
          // Numeric ID, freshman account
          result.freshmen.push(memberId);
        }
      }
    });

    return result;
  }
}
