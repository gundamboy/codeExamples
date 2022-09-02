package com.ragingclaw.mtgcubedraftsimulator.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.firebase.ui.auth.AuthUI;
import com.google.android.gms.auth.api.signin.GoogleSignIn;
import com.google.android.gms.auth.api.signin.GoogleSignInClient;
import com.google.android.gms.auth.api.signin.GoogleSignInOptions;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseAuthUserCollisionException;
import com.google.firebase.auth.FirebaseUser;
import com.ragingclaw.mtgcubedraftsimulator.R;
import com.ragingclaw.mtgcubedraftsimulator.fragments.CreateAccountFragment;
import com.ragingclaw.mtgcubedraftsimulator.fragments.EmailPasswordFragment;
import com.ragingclaw.mtgcubedraftsimulator.fragments.LoginFragment;

import java.util.Arrays;
import java.util.List;

import butterknife.ButterKnife;
import timber.log.Timber;

public class LoginActivity extends AppCompatActivity implements
        LoginFragment.OnFragmentInteractionListener,
        EmailPasswordFragment.OnFragmentInteractionListener,
        CreateAccountFragment.OnFragmentInteractionListener {

    public static final String ANONYMOUS = "anonymous";
    public static final int RC_SIGN_IN = 1;
    private String mUsername;
    private FirebaseAuth mAuth;
    private FirebaseUser user;
    private FirebaseAuth.AuthStateListener mAuthStateListener;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        ButterKnife.bind(this);

        // Initialize FireBase Auth
        mAuth = FirebaseAuth.getInstance();
        mUsername = ANONYMOUS;

        mAuthStateListener = new FirebaseAuth.AuthStateListener() {
            @Override
            public void onAuthStateChanged(@NonNull FirebaseAuth firebaseAuth) {
                FirebaseUser theUser = firebaseAuth.getCurrentUser();
                if(theUser != null){
                    //user is signed in
                    onSignedInInitialize(theUser.getDisplayName());
                } else {
                    //User is signed out
                    onSignedOutCleanup();

                    List<AuthUI.IdpConfig> providers = Arrays.asList(
                            new AuthUI.IdpConfig.EmailBuilder().build(),
                            new AuthUI.IdpConfig.GoogleBuilder().build()
                    );
                    startActivityForResult(
                            AuthUI.getInstance()
                                    .createSignInIntentBuilder()
                                    .setIsSmartLockEnabled(false)
                                    .setAvailableProviders(providers)
                                    .build(),
                            RC_SIGN_IN);
                }
            }
        };
    }

    private void onSignedInInitialize(String username){
        mUsername = username;
//        Intent intent = new Intent(this, MainActivity.class);
//        startActivity(intent);
//        finish();
    }

    private void onSignedOutCleanup(){
        mUsername = ANONYMOUS;
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == RC_SIGN_IN) {
            if (resultCode == RESULT_OK) {
                loggedIn();
            } else if (resultCode == RESULT_CANCELED) {
                Toast.makeText(this, "Sign in canceled.", Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }


    @Override
    public void onFragmentInteraction(View view, String message) {


    }

    @Override
    public void onEmailFragmentInteraction(String email, String password) {
        mAuth.signInWithEmailAndPassword(email, password)
                .addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
                    @Override
                    public void onComplete(@NonNull Task<AuthResult> task) {
                        if (task.isSuccessful()) {
                            // Sign in success, go to the MainActivity
                            user = mAuth.getCurrentUser();
                            loggedIn();
                        } else {
                            // If sign in fails, display a message to the user.
                            View toastView = getLayoutInflater().inflate(R.layout.custom_toast_view, null);
                            TextView emailSignInErrorToast = toastView.findViewById(R.id.emailSignInErrorToast);
                            emailSignInErrorToast.setVisibility(View.VISIBLE);
                            Toast toast = new Toast(getApplicationContext());
                            toast.setView(toastView);
                            toast.setDuration(Toast.LENGTH_LONG);
                            toast.setGravity(Gravity.BOTTOM, 0, 500);
                            toast.show();
                        }
                    }
                });
    }

    @Override
    public void onCreateAccountFragmentInteraction(String email, String password) {
        mAuth.createUserWithEmailAndPassword(email, password).addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
            @Override
            public void onComplete(@NonNull Task<AuthResult> task) {
                if(task.isSuccessful()) {
                    user = mAuth.getCurrentUser();

                } else {
                    if (task.getException() instanceof FirebaseAuthUserCollisionException) {
                        View toastView = getLayoutInflater().inflate(R.layout.custom_toast_view, null);
                        TextView accountAlreadyExistsErrorToast = toastView.findViewById(R.id.accountAlreadyExistsErrorToast);
                        accountAlreadyExistsErrorToast.setVisibility(View.VISIBLE);
                        Toast toast = new Toast(getApplicationContext());
                        toast.setView(toastView);
                        toast.setDuration(Toast.LENGTH_LONG);
                        toast.setGravity(Gravity.BOTTOM, 0, 500);
                        toast.show();
                    }
                }
            }
        });
    }

    private void googleSignIn() {

        GoogleSignInOptions gso = new GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
                .requestIdToken(getString(R.string.default_web_client_id))
                .requestEmail()
                .build();

        GoogleSignInClient mGoogleSignInClient = GoogleSignIn.getClient(this, gso);
        mAuth = FirebaseAuth.getInstance();

        Intent signInIntent = mGoogleSignInClient.getSignInIntent();
        startActivityForResult(signInIntent, RC_SIGN_IN);

    }

    private void loggedIn() {
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
        finish();
    }

    @Override
    protected void onResume() {
        super.onResume();
        //attach authStateListener
        mAuth.addAuthStateListener(mAuthStateListener);
    }

    @Override
    protected void onPause() {
        super.onPause();
        //detach authStateListener
        if(mAuthStateListener != null) {
            mAuth.removeAuthStateListener(mAuthStateListener);
        }
    }


}