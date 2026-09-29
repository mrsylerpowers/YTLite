#import <Foundation/Foundation.h>

#if __has_include(<roothide.h>)
#import <roothide.h>
#else
// Fallback for builds without the roothide headers (plain Theos, sideloaded app builds).
static inline NSString * _Nonnull jbroot(NSString * _Nonnull path) { return path; }
#endif

NS_ASSUME_NONNULL_BEGIN

@interface NSBundle (YTLite)

// Returns YTLite default bundle. Supports rootless if defined in compilation parameters
@property (class, nonatomic, readonly) NSBundle *ytl_defaultBundle;

@end

NS_ASSUME_NONNULL_END
