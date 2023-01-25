package x2;

import java.util.Base64;
public class X {
        static {
            System.loadLibrary("libadlemx.so");
        }
        public static String strrrr(){
        return System.getProperty("java.library.path");
        }
public static String m0do(String str) {
return Base64.getEncoder().encodeToString(x01(str).getBytes());
}
public static native String x01(String str);
    }
