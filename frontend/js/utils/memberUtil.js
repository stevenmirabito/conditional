export default class MemberUtil {
  static splitFreshmenUpperclassmen(memberIds) {
    const result = {
      freshmen: [],
      upperclassmen: [],
    };

    memberIds.forEach((memberId) => {
      if (memberId) {
        if (isNaN(memberId)) {
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
