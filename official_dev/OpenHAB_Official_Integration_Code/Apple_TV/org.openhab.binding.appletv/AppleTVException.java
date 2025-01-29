
package org.openhab.binding.appletv.internal;

import java.text.MessageFormat;

import org.eclipse.jdt.annotation.NonNullByDefault;


@NonNullByDefault
public class AppleTVException extends Exception {
    private static final long serialVersionUID = 7214176461907613559L;

    
    // public MagentaTVException(String message, Object... a) {
    // super(MessageFormat.format(message, a));

    public AppleTVException(String message) {
        super(message);
    }

    /**
     * Constructor. Creates new instance of MagentaTVException
     * Beside constructing a new object it also outputs the exception to the log (INFO) and the stack trace (TRACE)
     *
     * @param cause the cause. (A null value is permitted, and indicates that the
     *                  cause is nonexistent or unknown.)
     */
    public AppleTVException(Throwable cause) {
        super(cause);
    }

    /**
     * Constructor. Creates new instance of MagentaTVException
     * Beside constructing a new object it also outputs the exception to the log (INFO) and the stack trace (TRACE)
     *
     * @param message the detail message.
     * @param cause   the cause. (A null value is permitted, and indicates that the
     *                    cause is nonexistent or unknown.)
     */
    public AppleTVException(Throwable cause, String message, Object... a) {
        super(MessageFormat.format(message, a), cause);
    }

    static public String toString(Throwable e) {
        return e.getMessage() + "\n" + stackTrace(e);
    }

    static public String stackTrace(Throwable e) {
        StringBuilder sb = new StringBuilder();
        for (StackTraceElement s : e.getStackTrace()) {
            sb.append(s.toString()).append("\n");
        }
        return "Stack Trace:\n" + sb.toString();
    }

}
